// license:BSD-3-Clause
// copyright-holders:Curt Coder
/**********************************************************************

    Micro Peripherals Floppy Disk Interface emulation

**********************************************************************/

#pragma once

#ifndef __MICRO_PERIPHERALS_FLOPPY_DISK_INTERFACE__
#define __MICRO_PERIPHERALS_FLOPPY_DISK_INTERFACE__

#include "exp.h"



//**************************************************************************
//  TYPE DEFINITIONS
//**************************************************************************

// ======================> micro_peripherals_floppy_disk_interface_t

class micro_peripherals_floppy_disk_interface_t : public device_t,
													public device_ql_expansion_card_interface
{
public:
	// construction/destruction
	micro_peripherals_floppy_disk_interface_t(const machine_config &mconfig, const char *tag, device_t *owner, uint32_t clock);

	// optional information overrides
	virtual const tiny_rom_entry *device_rom_region() const override;

protected:
	// device-level overrides
	virtual void device_start() override;

	// device_ql_expansion_card_interface overrides
	virtual uint8_t read(address_space &space, offs_t offset, uint8_t data) override;
	virtual void write(address_space &space, offs_t offset, uint8_t data) override;
};



// device type definition
extern const device_type MICRO_PERIPHERALS_FLOPPY_DISK_INTERFACE;



#endif
