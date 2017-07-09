// license:LGPL-2.1+
// copyright-holders:David Haywood, Angelo Salese, ElSemi
//**************************************************************************
//  TYPE DEFINITIONS
//**************************************************************************

struct l7a1045_voice
{
	l7a1045_voice() : end(0), mode(false),
						pos(0),
		frac(0), l_volume(0), r_volume(0)
	{
		//memset(regs, 0, sizeof(uint32_t)*8);
		start = 0;
	}

	uint32_t start;
	uint32_t end;
	bool mode;
	uint32_t pos;
	uint32_t frac;
	uint16_t l_volume;
	uint16_t r_volume;
};

// ======================> l7a1045_sound_device

class l7a1045_sound_device : public device_t,
							public device_sound_interface
{
public:
	l7a1045_sound_device(const machine_config &mconfig, const char *tag, device_t *owner, uint32_t clock);
	~l7a1045_sound_device() { }

//  void set_base(int8_t* base) { m_base = base; }

	DECLARE_WRITE16_MEMBER( l7a1045_sound_w );
	DECLARE_READ16_MEMBER( l7a1045_sound_r );

protected:
	// device-level overrides
	virtual void device_start() override;

	// sound stream update overrides
	virtual void sound_stream_update(sound_stream &stream, stream_sample_t **inputs, stream_sample_t **outputs, int samples) override;

private:
	sound_stream *m_stream;
	l7a1045_voice m_voice[32];
	uint32_t    m_key;
	required_region_ptr<uint8_t> m_rom;

	uint8_t m_audiochannel;
	uint8_t m_audioregister;

	struct l7a1045_48bit_data {
		uint16_t dat[3];
	};

	l7a1045_48bit_data m_audiodat[0x10][0x20];

	DECLARE_WRITE16_MEMBER(sound_select_w);
	DECLARE_WRITE16_MEMBER(sound_data_w);
	DECLARE_READ16_MEMBER(sound_data_r);
	DECLARE_WRITE16_MEMBER(sound_status_w);
};

extern const device_type L7A1045;