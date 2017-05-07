// license:BSD-3-Clause
// copyright-holders:Curt Coder
/**********************************************************************

    COMX-35 F&M EPROM Card emulation

**********************************************************************/

#pragma once

#ifndef __COMX_EPR__
#define __COMX_EPR__

#include "exp.h"



//**************************************************************************
//  TYPE DEFINITIONS
//**************************************************************************

// ======================> comx_epr_device

class comx_epr_device : public device_t,
						public device_comx_expansion_card_interface
{
public:
	// construction/destruction
	comx_epr_device(const machine_config &mconfig, const char *tag, device_t *owner, uint32_t clock);

	// optional information overrides
	virtual const tiny_rom_entry *device_rom_region() const override;

protected:
	// device-level overrides
	virtual void device_start() override;
	virtual void device_reset() override;

	// device_comx_expansion_card_interface overrides
	virtual uint8_t comx_mrd_r(address_space &space, offs_t offset, int *extrom) override;
	virtual void comx_io_w(address_space &space, offs_t offset, uint8_t data) override;

private:
	required_memory_region m_rom;
	required_memory_region m_eprom;

	uint8_t m_select;
};


// device type definition
extern const device_type COMX_EPR;


#endif
