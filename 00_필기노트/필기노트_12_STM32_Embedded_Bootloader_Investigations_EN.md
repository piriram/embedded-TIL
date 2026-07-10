# Ch.12 STM32 Embedded Bootloader Investigations

Purpose: English handwritten-note version for STM32 bootloader debugging

Rules:

- Focus on technical English expressions
- Keep each sentence short enough to explain in an interview
- Blue: title, section number, key term
- Black: explanation and example
- Red: warning, interview caution, common mistake
- Use this note to connect boot mode, AN2606, option bytes, pins, and communication interfaces

## Page 1: What Is the STM32 Embedded Bootloader?

<span style="color:#1d4ed8">Topic: Embedded bootloader investigation</span><br>
<span style="color:#1d4ed8">1. Core idea</span><br>
<span style="color:#111827">All STM32 MCUs include an embedded bootloader in system memory.</span><br>
<span style="color:#111827">This bootloader allows firmware programming through supported interfaces.</span><br>
<span style="color:#111827">Examples include USART, I2C, SPI, USB, and CAN, depending on the MCU family.</span><br>
<span style="color:#111827">The boot mode decides whether the MCU starts from user Flash, SRAM, or system memory.</span><br>
<span style="color:#dc2626">Important: bootloader behavior is device-specific. Always check the exact MCU documents.</span><br>
<br>
<span style="color:#1d4ed8">2. Documents to check</span><br>
<span style="color:#111827">Reference manual: explains boot mode configuration for the selected MCU.</span><br>
<span style="color:#111827">AN2606: lists the bootloader activation patterns and supported interfaces.</span><br>
<span style="color:#111827">Board user manual: shows where BOOT0 and connector pins are located.</span><br>
<span style="color:#111827">These three documents must be used together.</span><br>
<span style="color:#dc2626">Do not guess BOOT0 or bootloader pins from another board.</span><br>
<br>
<span style="color:#1d4ed8">3. Boot mode can depend on</span><br>
<span style="color:#111827">BOOT0 pin level.</span><br>
<span style="color:#111827">Option byte values.</span><br>
<span style="color:#111827">Empty Flash check mechanism.</span><br>
<span style="color:#111827">Software boot configuration, depending on the MCU.</span><br>
<span style="color:#dc2626">Interview point: boot mode is not controlled by only one thing.</span><br>

## Page 2: Activating the Bootloader

<span style="color:#1d4ed8">4. Example target</span><br>
<span style="color:#111827">The video uses an STM32G474 Nucleo board.</span><br>
<span style="color:#111827">The same investigation principle applies to other STM32 families.</span><br>
<span style="color:#111827">However, the exact activation pattern and interface list can differ.</span><br>
<span style="color:#dc2626">Use the example as a method, not as a universal pin map.</span><br>
<br>
<span style="color:#1d4ed8">5. Activation pattern example</span><br>
<span style="color:#111827">The speaker checks AN2606 and finds the activation pattern for the target MCU.</span><br>
<span style="color:#111827">For this board, the selected pattern requires several conditions.</span><br>
<span style="color:#111827">BOOT_LOCK option bit must not lock the boot path.</span><br>
<span style="color:#111827">nBOOT1 option bit must be set to the required value.</span><br>
<span style="color:#111827">BOOT0 pin must be set to high.</span><br>
<span style="color:#111827">nSWBOOT0 option bit must match the required configuration.</span><br>
<span style="color:#dc2626">Common mistake: setting BOOT0 only and ignoring option bytes.</span><br>
<br>
<span style="color:#1d4ed8">6. Checking option bytes in CubeProgrammer</span><br>
<span style="color:#111827">Open STM32CubeProgrammer.</span><br>
<span style="color:#111827">Connect to the board through ST-LINK.</span><br>
<span style="color:#111827">Open the Option Bytes tab.</span><br>
<span style="color:#111827">Check security-related boot lock settings.</span><br>
<span style="color:#111827">Check user configuration values such as nBOOT1 and nSWBOOT0.</span><br>
<span style="color:#111827">Then set the physical BOOT0 pin level according to the board manual.</span><br>
<span style="color:#dc2626">Option bytes are part of the boot configuration, not just security settings.</span><br>

## Page 3: How to Verify Bootloader Activation

<span style="color:#1d4ed8">7. Main verification method</span><br>
<span style="color:#111827">Check the Program Counter value.</span><br>
<span style="color:#111827">If the bootloader is active, the Program Counter should be in the system memory address range.</span><br>
<span style="color:#111827">If the user application is active, the Program Counter should be in the Flash address range.</span><br>
<span style="color:#111827">The address ranges are described in the reference manual.</span><br>
<span style="color:#dc2626">This is stronger evidence than just saying “the bootloader seems to run.”</span><br>
<br>
<span style="color:#1d4ed8">8. Example interpretation</span><br>
<span style="color:#111827">BOOT0 high + required option bytes → reset → Program Counter in system memory.</span><br>
<span style="color:#111827">BOOT0 low → reset → Program Counter in user Flash.</span><br>
<span style="color:#111827">This confirms that the boot mode selection is working.</span><br>
<span style="color:#111827">It also proves that the debugger can be used as an investigation tool.</span><br>
<span style="color:#dc2626">Interview point: verify boot mode by address range, not by assumption.</span><br>
<br>
<span style="color:#1d4ed8">9. Key English sentence</span><br>
<span style="color:#111827">I verified bootloader activation by checking whether the Program Counter was located in the system memory range.</span><br>
<span style="color:#111827">When BOOT0 was low, the Program Counter moved to the user Flash range after reset.</span><br>
<span style="color:#dc2626">Practice this sentence aloud.</span><br>

## Page 4: Bootloader Communication Interfaces

<span style="color:#1d4ed8">10. Supported interfaces</span><br>
<span style="color:#111827">AN2606 lists the supported bootloader interfaces for each STM32 device.</span><br>
<span style="color:#111827">For the example G4 device, supported interfaces include multiple USARTs, I2C, SPI, and USB.</span><br>
<span style="color:#111827">Each interface has specific pins.</span><br>
<span style="color:#111827">The board design must route the expected pins correctly.</span><br>
<span style="color:#dc2626">If the interface pins are wrong, the bootloader may be active but unreachable.</span><br>
<br>
<span style="color:#1d4ed8">11. First debugging advice</span><br>
<span style="color:#111827">If bootloader communication fails, first test the same hardware path with a simple user application.</span><br>
<span style="color:#111827">For example, create a simple USART application before blaming the bootloader.</span><br>
<span style="color:#111827">This checks whether the board routing, connector, and pins are correct.</span><br>
<span style="color:#111827">It separates hardware-path problems from bootloader-state problems.</span><br>
<span style="color:#dc2626">Good debugging starts by isolating the failure domain.</span><br>
<br>
<span style="color:#1d4ed8">12. Interface scanning behavior</span><br>
<span style="color:#111827">The embedded bootloader scans supported interfaces after activation.</span><br>
<span style="color:#111827">When it detects activity on one interface, it stops scanning other interfaces.</span><br>
<span style="color:#111827">Then it enters a loop waiting on the detected interface.</span><br>
<span style="color:#111827">This can block communication on the interface that the user actually wanted.</span><br>
<span style="color:#dc2626">This is the key lesson of the video.</span><br>

## Page 5: Wrong Interface Detection Problem

<span style="color:#1d4ed8">13. Failure scenario</span><br>
<span style="color:#111827">The user wants to communicate with the bootloader through USART2.</span><br>
<span style="color:#111827">Before USART2 communication starts, another pin toggles.</span><br>
<span style="color:#111827">The bootloader interprets that activity as USART1 activity.</span><br>
<span style="color:#111827">The bootloader then waits on USART1.</span><br>
<span style="color:#111827">Communication through USART2 fails until the next reset.</span><br>
<span style="color:#dc2626">A random pin transition during power-up can select the wrong bootloader interface.</span><br>
<br>
<span style="color:#1d4ed8">14. Why this matters in product design</span><br>
<span style="color:#111827">During board power-up, some external signals may toggle unexpectedly.</span><br>
<span style="color:#111827">If those pins are connected to bootloader-supported interfaces, the bootloader may lock onto the wrong interface.</span><br>
<span style="color:#111827">This can make production programming or field recovery unreliable.</span><br>
<span style="color:#111827">The bootloader cannot be modified because it is embedded by ST.</span><br>
<span style="color:#dc2626">Bootloader interface behavior must be considered during product definition.</span><br>
<br>
<span style="color:#1d4ed8">15. Practical design implication</span><br>
<span style="color:#111827">Avoid unwanted activity on bootloader interface pins during reset and startup.</span><br>
<span style="color:#111827">Check pull-ups, pull-downs, external devices, and connector states.</span><br>
<span style="color:#111827">Make sure the intended bootloader interface is reachable and quiet until communication starts.</span><br>
<span style="color:#dc2626">Bootloader access is part of board-level design, not only firmware design.</span><br>

## Page 6: Investigating Which Interface Was Activated

<span style="color:#1d4ed8">16. Investigation strategy</span><br>
<span style="color:#111827">If communication fails, identify which bootloader interface was initialized.</span><br>
<span style="color:#111827">Use AN2606 to list all possible bootloader interfaces.</span><br>
<span style="color:#111827">Use the reference manual to find the base address and register size of each peripheral.</span><br>
<span style="color:#111827">Dump the peripheral register values through the debug link.</span><br>
<span style="color:#111827">Compare register values before and after communication attempts.</span><br>
<span style="color:#dc2626">This is register-level debugging of the bootloader state.</span><br>
<br>
<span style="color:#1d4ed8">17. Why command line is useful</span><br>
<span style="color:#111827">The video recommends using STM32CubeProgrammer command line.</span><br>
<span style="color:#111827">The command line can dump register contents from several interfaces.</span><br>
<span style="color:#111827">This makes it easier to compare USART, I2C, SPI, and USB register states.</span><br>
<span style="color:#111827">The debug connection should not reset the board if the current bootloader state must be preserved.</span><br>
<span style="color:#dc2626">If you reset the board too early, you may destroy the evidence.</span><br>
<br>
<span style="color:#1d4ed8">18. Evidence from register changes</span><br>
<span style="color:#111827">If USART2 was used, USART2 registers show communication-related changes.</span><br>
<span style="color:#111827">If a USART1 pin was toggled, USART1 registers show signs of attempted communication.</span><br>
<span style="color:#111827">If USB is plugged in, USB registers show connection activity.</span><br>
<span style="color:#111827">These changes reveal which interface the bootloader selected.</span><br>
<span style="color:#dc2626">The selected interface may not be the interface you expected.</span><br>

## Page 7: Workarounds and Design Choices

<span style="color:#1d4ed8">19. Possible workaround 1</span><br>
<span style="color:#111827">Jump to the embedded bootloader from the user application.</span><br>
<span style="color:#111827">This allows the application to control when the bootloader is entered.</span><br>
<span style="color:#111827">It can also ensure that only the intended interface pins are active.</span><br>
<span style="color:#111827">This method is described in AN2606 for supported devices.</span><br>
<span style="color:#dc2626">This is not possible or identical on every STM32 chip.</span><br>
<br>
<span style="color:#1d4ed8">20. Possible workaround 2</span><br>
<span style="color:#111827">Implement a custom bootloader.</span><br>
<span style="color:#111827">A custom bootloader can define exactly which interface and protocol to use.</span><br>
<span style="color:#111827">ST Cube firmware packages include bootloader examples for some devices.</span><br>
<span style="color:#111827">This gives more control but increases firmware complexity.</span><br>
<span style="color:#dc2626">Custom bootloader design must include safety, recovery, and update-failure handling.</span><br>
<br>
<span style="color:#1d4ed8">21. Related protocol documents</span><br>
<span style="color:#111827">AN2606 explains system memory boot mode and activation patterns.</span><br>
<span style="color:#111827">Other ST application notes explain bootloader communication protocols.</span><br>
<span style="color:#111827">The relevant protocol document depends on the selected interface.</span><br>
<span style="color:#111827">For example, USART, I2C, SPI, USB DFU, and CAN have different protocol details.</span><br>
<span style="color:#dc2626">Do not mix boot activation rules with communication protocol rules.</span><br>

## Technical Vocabulary

<span style="color:#1d4ed8">embedded bootloader</span><br>
<span style="color:#111827">A built-in ST bootloader stored in system memory.</span><br>
<br>
<span style="color:#1d4ed8">activation pattern</span><br>
<span style="color:#111827">A required combination of pins and option bytes that makes the MCU boot into system memory.</span><br>
<br>
<span style="color:#1d4ed8">option byte</span><br>
<span style="color:#111827">A non-volatile configuration value that controls device behavior such as boot configuration or protection.</span><br>
<br>
<span style="color:#1d4ed8">Program Counter</span><br>
<span style="color:#111827">A CPU register that contains the address of the instruction currently being executed or about to be executed.</span><br>
<br>
<span style="color:#1d4ed8">system memory</span><br>
<span style="color:#111827">A protected memory area that contains the embedded bootloader.</span><br>
<br>
<span style="color:#1d4ed8">user Flash</span><br>
<span style="color:#111827">Flash memory where the user application firmware is stored.</span><br>
<br>
<span style="color:#1d4ed8">DFU</span><br>
<span style="color:#111827">Device Firmware Upgrade, commonly used for USB firmware update mode.</span><br>
<br>
<span style="color:#1d4ed8">register dump</span><br>
<span style="color:#111827">Reading raw peripheral register values to inspect hardware or firmware state.</span><br>

## 30-Second English Explanation

<span style="color:#1d4ed8">Interview answer</span><br>
<span style="color:#111827">STM32 MCUs include an embedded bootloader in system memory.</span><br>
<span style="color:#111827">To activate it correctly, I need to check the MCU reference manual and AN2606 because the required pin and option-byte pattern depends on the device.</span><br>
<span style="color:#111827">After entering boot mode, I can verify activation by checking whether the Program Counter is in the system memory address range.</span><br>
<span style="color:#111827">If bootloader communication fails, one possible reason is that activity on another supported interface made the bootloader lock onto the wrong interface.</span><br>
<span style="color:#111827">In that case, I would inspect the possible interface pins and dump peripheral registers to see which interface was initialized.</span><br>
<span style="color:#dc2626">Close with: This shows that bootloader debugging requires both firmware and board-level thinking.</span><br>

## Practice Questions

<span style="color:#1d4ed8">Q1. Where is the STM32 embedded bootloader located?</span><br>
<span style="color:#111827">It is located in system memory inside the STM32 device.</span><br>
<br>
<span style="color:#1d4ed8">Q2. Which documents should be checked for bootloader activation?</span><br>
<span style="color:#111827">The MCU reference manual, AN2606, and the board user manual.</span><br>
<br>
<span style="color:#1d4ed8">Q3. How can you verify that the bootloader is active?</span><br>
<span style="color:#111827">Check whether the Program Counter is in the system memory address range.</span><br>
<br>
<span style="color:#1d4ed8">Q4. Why can communication through the expected interface fail?</span><br>
<span style="color:#111827">Because the bootloader may have detected activity on another interface and stopped scanning.</span><br>
<br>
<span style="color:#1d4ed8">Q5. How can you investigate the selected interface?</span><br>
<span style="color:#111827">List possible interfaces from AN2606, find register addresses in the reference manual, and dump the peripheral registers.</span><br>
<br>
<span style="color:#1d4ed8">Q6. Why is this important for product design?</span><br>
<span style="color:#111827">Because unintended pin activity during startup can make bootloader recovery or production programming unreliable.</span><br>

## Source

<span style="color:#1d4ed8">Original video</span><br>
<span style="color:#111827">STM32 boot and startup tips - Embedded bootloader investigations</span><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=kTMjjED8ErA">https://www.youtube.com/watch?v=kTMjjED8ErA</a><br>
<br>
<span style="color:#1d4ed8">Related document</span><br>
<span style="color:#111827">AN2606 - STM32 microcontroller system memory boot mode</span><br>
<span style="color:#dc2626">Use AN2606 to confirm activation patterns and available bootloader interfaces for each STM32 family.</span><br>
