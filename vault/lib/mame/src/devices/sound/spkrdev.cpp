// license:BSD-3-Clause
// copyright-holders:Nicola Salmoria
/***************************************************************************

    speaker.c

    Sound driver to emulate a simple speaker,
    driven by one or more output bits

    Original author: (unsigned)
    Filtering: Anders Hallstr?m
****************************************************************************/

/* Discussion of oversampling and anti-alias filtering: (Anders Hallstr?m)
 *
 * This driver is for machines that directly control
 * one or more simple digital-to-analog converters (DAC)
 * connected to one or more audio outputs (such as analog amp + speaker).
 * Currently only 1-bit DAC is supported via the interface to this module.
 *
 * Frequently such machines would oversample the DAC
 * in order to overcome the limited DAC resolution.
 * For faithful reproduction of the sound, this must be carefully handled
 * with anti-alias filtering when converting a high-rate low-resolution signal
 * to a moderate-rate high-resolution signal suitable for the DAC in the emulator's sound card.
 * (Originally, removal of any redundant high frequency content occurred on the analog side
 *  with no aliasing effects.)
 *
 * The most straightforward, naive way to handle this is to use two streams;
 * stream 1 modeling the native audio, with a sampling rate that allows for
 * accurate representation of over-sampling, i.e. the sampling rate should match
 * the clock frequency of the audio generating device (such as the CPU).
 * Stream 1 is connected to stream 2, which is concerned with feeding the sound card.
 * The stream system has features to handle rate conversion from stream 1 to 2.
 *
 * I tried it out of curiosity; it works fine conceptually, but
 *  - it puts an unnecessary burden on system resources
 *  - sound quality is still not satisfactory, though better than without anti-alias
 *  - "stream 1" properties are machine specific and so should be configured
 *    individually in each machine driver using this approach.
 *    This can also be seen as an advantage for flexibility, though.
 *
 * Instead, dedicated filtering is implemented in this module,
 * in a machine-neutral way (based on machine time and external -samplerate only).
 *
 * The basic average filter has the advantage that it can be used without
 * explicitly generating all samples in "stream 1". However,
 * it is poor for anti-alias filtering.
 * Therefore, average filtering is combined with windowed sinc.
 *
 * Virtual stream 1: Samples in true machine time.
 * Any sampling rate up to attotime resolution is implicitly supported.
 * -> average filtering over each stream 2 sample ->
 * Virtual stream 2: Intermediate representation.
 * Sample rate = RATE_MULTIPLIER * stream 3 sample rate.
 * If effective rate of stream 1 exceeds rate of stream 2,
 * some aliasing distorsion is introduced in this step because the average filtering is a compromise.
 * The distorsion is however mostly in the higher frequencies.
 * -> low-pass anti-alias filtering with kernel ampl[] ->
 * -> down-sampling ->
 * Actual stream 3: channel output generated by speaker_sound_update().
 * Sample rate = device sample rate = configured "-samplerate".
 *
 * In the speaker_state data structure,
 *    "intermediate samples" refers to "stream 2"
 *    "channel samples" refers to "stream 3"
 */

/* IMPROVEMENTS POSSIBLE:
 * - Make filter length a run-time configurable parameter. min=1 max=1000 or something
 * - Optimize cutoff freq automatically after filter length, or configurable too
 * - Generalise this approach to other DAC-based sound types if susceptible to aliasing
 */

#include "emu.h"
#include "sound/spkrdev.h"


static const int16_t default_levels[2] = {0, 32767};

// Internal oversampling factor (interm. samples vs stream samples)
static const int RATE_MULTIPLIER = 4;


const device_type SPEAKER_SOUND = device_creator<speaker_sound_device>;

template class device_finder<speaker_sound_device, false>;
template class device_finder<speaker_sound_device, true>;


speaker_sound_device::speaker_sound_device(const machine_config &mconfig, const char *tag, device_t *owner, uint32_t clock)
	: device_t(mconfig, SPEAKER_SOUND, "Filtered 1-bit DAC", tag, owner, clock, "speaker_sound", __FILE__)
	, device_sound_interface(mconfig, *this)
	, m_num_levels(2)
	, m_levels(default_levels)
{
}

//-------------------------------------------------
//  device_start - device-specific startup
//-------------------------------------------------

void speaker_sound_device::device_start()
{
	int i;
	double x;

	m_channel = machine().sound().stream_alloc(*this, 0, 1, machine().sample_rate());

	m_level = 0;
	for (i = 0; i < FILTER_LENGTH; i++)
		m_composed_volume[i] = 0;

	m_composed_sample_index = 0;
	m_last_update_time = machine().time();
	m_channel_sample_period = HZ_TO_ATTOSECONDS(machine().sample_rate());
	m_channel_sample_period_secfrac = ATTOSECONDS_TO_DOUBLE(m_channel_sample_period);
	m_interm_sample_period = m_channel_sample_period / RATE_MULTIPLIER;
	m_interm_sample_period_secfrac = ATTOSECONDS_TO_DOUBLE(m_interm_sample_period);
	m_channel_last_sample_time = m_channel->sample_time();
	m_channel_next_sample_time = m_channel_last_sample_time + attotime(0, m_channel_sample_period);
	m_next_interm_sample_time = m_channel_last_sample_time + attotime(0, m_interm_sample_period);
	m_interm_sample_index = 0;
	m_prevx = m_prevy = 0.0;

	/* Note: To avoid time drift due to floating point inaccuracies,
	 * it is good if the speaker time synchronizes itself with the stream timing regularly.
	 */

	/* Compute filter kernel; */
	/* (Done for each device though the data is shared...
	 *  No problem really, but should be done as part of system init if I knew how)
	 */
#if 1
	/* This is an approximated sinc (a perfect sinc makes an ideal low-pass filter).
	 * FILTER_STEP determines the cutoff frequency,
	 * which should be below the Nyquist freq, i.e. half the sample rate.
	 * Smaller step => kernel extends in time domain => lower cutoff freq
	 * In this case, with sinc, filter step PI corresponds to the Nyq. freq.
	 * Since we do not get a perfect filter => must lower the cutoff freq some more.
	 * For example, step PI/(2*RATE_MULTIPLIER) corresponds to cutoff freq = sample rate / 4;
	 *    With -samplerate 48000, cutoff freq is ca 12kHz while the Nyq. freq is 24kHz.
	 *    With -samplerate 96000, cutoff freq is ca 24kHz while the Nyq. freq is 48kHz.
	 * For a steeper, more efficient filter, increase FILTER_LENGTH at the expense of CPU usage.
	 */
#define FILTER_STEP  (M_PI / 2 / RATE_MULTIPLIER)
	/* Distribute symmetrically on x axis; center has x=0 if length is odd */
	for (i = 0,             x = (0.5 - FILTER_LENGTH / 2.) * FILTER_STEP;
			i < FILTER_LENGTH;
			i++,                x += FILTER_STEP)
	{
		if (x == 0)
			m_ampl[i] = 1;
		else
			m_ampl[i] = sin(x) / x;
	}
#else
	/* Trivial average filter with poor frequency cutoff properties;
	 * First zero (frequency where amplification=0) = sample rate / filter length
	 * Cutoff frequency approx <= first zero / 2
	 */
	for (i = 0, i < FILTER_LENGTH; i++)
		m_ampl[i] = 1;
#endif

	save_item(NAME(m_level));
	save_item(NAME(m_composed_volume));
	save_item(NAME(m_composed_sample_index));
	save_item(NAME(m_channel_last_sample_time));
	save_item(NAME(m_interm_sample_index));
	save_item(NAME(m_last_update_time));
	save_item(NAME(m_prevx));
	save_item(NAME(m_prevy));

	machine().save().register_postload(save_prepost_delegate(FUNC(speaker_sound_device::speaker_postload), this));
}

void speaker_sound_device::device_reset()
{
	int i;

	m_level = 0;
	for (i = 0; i < FILTER_LENGTH; i++)
		m_composed_volume[i] = 0;

	m_composed_sample_index = 0;
	m_last_update_time = machine().time();
	m_channel_sample_period = HZ_TO_ATTOSECONDS(machine().sample_rate());
	m_channel_sample_period_secfrac = ATTOSECONDS_TO_DOUBLE(m_channel_sample_period);
	m_interm_sample_period = m_channel_sample_period / RATE_MULTIPLIER;
	m_interm_sample_period_secfrac = ATTOSECONDS_TO_DOUBLE(m_interm_sample_period);
	m_channel_last_sample_time = m_channel->sample_time();
	m_channel_next_sample_time = m_channel_last_sample_time + attotime(0, m_channel_sample_period);
	m_next_interm_sample_time = m_channel_last_sample_time + attotime(0, m_interm_sample_period);
	m_interm_sample_index = 0;
	m_prevx = m_prevy = 0.0;
}

void speaker_sound_device::speaker_postload()
{
	m_channel_next_sample_time = m_channel_last_sample_time + attotime(0, m_channel_sample_period);
	m_next_interm_sample_time = m_channel_last_sample_time + attotime(0, m_interm_sample_period);
}

//-------------------------------------------------
//  sound_stream_update - handle a stream update
//-------------------------------------------------

// This can be triggered by the core (based on emulated time) or via level_w().
void speaker_sound_device::sound_stream_update(sound_stream &stream, stream_sample_t **inputs, stream_sample_t **outputs, int samples)
{
	stream_sample_t *buffer = outputs[0];
	int volume = m_levels[m_level];
	double filtered_volume;
	attotime sampled_time = attotime::zero;

	if (samples > 0)
	{
		/* Prepare to update time state */
		sampled_time = attotime(0, m_channel_sample_period);
		if (samples > 1)
			sampled_time *= samples;

		/* Note: since the stream is in the process of being updated,
		 * stream->sample_time() will return the time before the update! (MAME 0.130)
		 * Avoid using it here in order to avoid a subtle dependence on the stream implementation.
		 */
	}

	if (samples-- > 0)
	{
		/* Note that first interm. sample may be composed... */
		filtered_volume = update_interm_samples_get_filtered_volume(volume);

		/* Composite volume is now quantized to the stream resolution */
		*buffer++ = (stream_sample_t)filtered_volume;

		/* Any additional samples will be homogeneous, however may need filtering across samples: */
		while (samples-- > 0)
		{
			filtered_volume = update_interm_samples_get_filtered_volume(volume);
			*buffer++ = (stream_sample_t)filtered_volume;
		}

		/* Update the time state */
		m_channel_last_sample_time += sampled_time;
		m_channel_next_sample_time = m_channel_last_sample_time + attotime(0, m_channel_sample_period);
		m_next_interm_sample_time = m_channel_last_sample_time + attotime(0, m_interm_sample_period);
		m_last_update_time = m_channel_last_sample_time;
	}
}



void speaker_sound_device::level_w(int new_level)
{
	int volume;
	attotime time;

	if (new_level == m_level)
		return;

	if (new_level < 0)
		new_level = 0;
	else
	if (new_level >= m_num_levels)
		new_level = m_num_levels - 1;

	volume = m_levels[m_level];
	time = machine().time();

	if (time < m_channel_next_sample_time)
	{
		/* Stream sample is yet unfinished, but we may have one or more interm. samples */
		update_interm_samples(time, volume);

		/* Do not forget to update speaker state before returning! */
		m_level = new_level;
		return;
	}
	/* Reaching here means such time has passed since last stream update
	 * that we can add at least one complete sample to the stream.
	 * The details have to be handled by speaker_sound_update()
	 */

	/* Force streams.c to update sound until this point in time now */
	m_channel->update();

	/* This is redundant because time update has to be done within speaker_sound_update() anyway,
	 * however this ensures synchronization between the speaker and stream timing:
	 */
	m_channel_last_sample_time = m_channel->sample_time();
	m_channel_next_sample_time = m_channel_last_sample_time + attotime(0, m_channel_sample_period);
	m_next_interm_sample_time = m_channel_last_sample_time + attotime(0, m_interm_sample_period);
	m_last_update_time = m_channel_last_sample_time;

	/* Assertion: time - last_update_time < channel_sample_period, i.e. time < channel_next_sample_time */

	/* The overshooting fraction of time will make zero, one or more interm. samples: */
	update_interm_samples(time, volume);

	/* Finally update speaker state before returning */
	m_level = new_level;

}


void speaker_sound_device::update_interm_samples(const attotime &time, int volume)
{
	double fraction;

	/* We may have completed zero, one or more interm. samples: */
	while (time >= m_next_interm_sample_time)
	{
		/* First interm. sample may be composed, subsequent samples will be homogeneous. */
		/* Treat all the same general way. */
		finalize_interm_sample(volume);
		init_next_interm_sample();
	}
	/* Depending on status above:
	 * a) Add latest fraction to unfinished composed sample
	 * b) The overshooting fraction of time will start a new composed sample
	 */
	fraction = make_fraction(time, m_last_update_time, m_interm_sample_period_secfrac);
	m_composed_volume[m_composed_sample_index] += volume * fraction;
	m_last_update_time = time;
}


double speaker_sound_device::update_interm_samples_get_filtered_volume(int volume)
{
	double filtered_volume, tempx;

	/* We may have one or more interm. samples to go */
	if (m_interm_sample_index < RATE_MULTIPLIER)
	{
		/* First interm. sample may be composed. */
		finalize_interm_sample(volume);

		/* Subsequent interm. samples will be homogeneous. */
		while (m_interm_sample_index + 1 < RATE_MULTIPLIER)
		{
			init_next_interm_sample();
			m_composed_volume[m_composed_sample_index] = volume;
		}
	}
	/* Important: next interm. sample not initialised yet, so that no data is destroyed before filtering... */
	filtered_volume = get_filtered_volume();
	init_next_interm_sample();
	/* Reset counter to next stream sample: */
	m_interm_sample_index = 0;

	/* simple DC blocker filter */
	tempx = filtered_volume;
	filtered_volume = tempx - m_prevx + 0.995 * m_prevy;
	m_prevx = tempx;
	m_prevy = filtered_volume;

	return filtered_volume;
}


void speaker_sound_device::finalize_interm_sample(int volume)
{
	double fraction;

	/* Fill the composed sample up if it was incomplete */
	fraction = make_fraction(m_next_interm_sample_time, m_last_update_time, m_interm_sample_period_secfrac);
	m_composed_volume[m_composed_sample_index] += volume * fraction;
	/* Update time state */
	m_last_update_time = m_next_interm_sample_time;
	m_next_interm_sample_time += attotime(0, m_interm_sample_period);

	/* For compatibility with filtering, do not incr. index and initialise next sample yet. */
}


void speaker_sound_device::init_next_interm_sample()
{
	/* Move the index and initialize next composed sample */
	m_composed_sample_index++;
	if (m_composed_sample_index >= FILTER_LENGTH)
		m_composed_sample_index = 0;
	m_composed_volume[m_composed_sample_index] = 0;

	m_interm_sample_index++;
	/* No limit check on interm_sample_index here - to be handled by caller */
}


inline double speaker_sound_device::make_fraction(const attotime &a, const attotime &b, double timediv)
{
	/* fraction = (a - b) / timediv */
	return (a - b).as_double() / timediv;
}


double speaker_sound_device::get_filtered_volume()
{
	double filtered_volume = 0;
	double ampsum = 0;
	int i, c;

	/* Filter over composed samples (each composed sample is already average filtered) */
	for (i = m_composed_sample_index + 1, c = 0; c < FILTER_LENGTH; i++, c++)
	{
		if (i >= FILTER_LENGTH) i = 0;
		filtered_volume += m_composed_volume[i] * m_ampl[c];
		ampsum += m_ampl[c];
	}
	filtered_volume /= ampsum;

	return filtered_volume;
}
