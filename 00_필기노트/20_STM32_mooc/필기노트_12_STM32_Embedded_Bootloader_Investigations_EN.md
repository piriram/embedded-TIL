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
<span style="color:#111827">a. All STM32 MCUs include an embedded bootloader in system memory.</span><br>
<span style="color:#111827">b. This bootloader allows firmware programming through supported interfaces.</span><br>
<span style="color:#111827">c. The boot mode decides whether the MCU starts from user Flash, SRAM, or system memory.</span><br>
<span style="color:#111827">- Example interfaces: USART, I2C, SPI, USB, CAN</span><br>
<span style="color:#dc2626">※ Bootloader behavior is device-specific. Always check the exact MCU documents</span><br>
<br>
<span style="color:#1d4ed8">2. Documents to check</span><br>
<span style="color:#111827">a. Reference manual explains boot mode configuration for the selected MCU.</span><br>
<span style="color:#111827">b. AN2606 lists bootloader activation patterns and supported interfaces.</span><br>
<span style="color:#111827">c. Board user manual shows where BOOT0 and connector pins are located.</span><br>
<span style="color:#111827">d. These three documents must be used together.</span><br>
<span style="color:#dc2626">※ Do not guess BOOT0 or bootloader pins from another board</span><br>
<br>
<span style="color:#1d4ed8">3. Boot mode can depend on</span><br>
<span style="color:#111827">a. BOOT0 pin level.</span><br>
<span style="color:#111827">b. Option byte values.</span><br>
<span style="color:#111827">c. Empty Flash check mechanism.</span><br>
<span style="color:#111827">d. Software boot configuration, depending on the MCU.</span><br>
<span style="color:#dc2626">※ Boot mode is not controlled by only one thing</span><br>

## Page 2: Activating the Bootloader

<span style="color:#1d4ed8">4. Example target</span><br>
<span style="color:#111827">a. The video uses an STM32G474 Nucleo board.</span><br>
<span style="color:#111827">b. The same investigation principle applies to other STM32 families.</span><br>
<span style="color:#111827">c. However, the exact activation pattern and interface list can differ.</span><br>
<span style="color:#dc2626">※ Use the example as a method, not as a universal pin map</span><br>
<br>
<span style="color:#1d4ed8">5. Activation pattern example</span><br>
<span style="color:#111827">a. The speaker checks AN2606 and finds the activation pattern for the target MCU.</span><br>
<span style="color:#111827">b. For this board, the selected pattern requires several conditions.</span><br>
<span style="color:#111827">c. BOOT_LOCK option bit must not lock the boot path.</span><br>
<span style="color:#111827">d. nBOOT1 option bit must be set to the required value.</span><br>
<span style="color:#111827">e. BOOT0 pin must be set to high.</span><br>
<span style="color:#111827">f. nSWBOOT0 option bit must match the required configuration.</span><br>
<span style="color:#dc2626">※ Common mistake: setting BOOT0 only and ignoring option bytes</span><br>
<br>
<span style="color:#1d4ed8">6. Checking option bytes in CubeProgrammer</span><br>
<span style="color:#111827">a. Open STM32CubeProgrammer.</span><br>
<span style="color:#111827">b. Connect to the board through ST-LINK.</span><br>
<span style="color:#111827">c. Open the Option Bytes tab.</span><br>
<span style="color:#111827">d. Check security-related boot lock settings.</span><br>
<span style="color:#111827">e. Check user configuration values such as nBOOT1 and nSWBOOT0.</span><br>
<span style="color:#111827">f. Set the physical BOOT0 pin level according to the board manual.</span><br>
<span style="color:#dc2626">※ Option bytes are part of boot configuration, not just security settings</span><br>

## Page 3: How to Verify Bootloader Activation

<span style="color:#1d4ed8">7. Main verification method</span><br>
<span style="color:#111827">a. Check the Program Counter value.</span><br>
<span style="color:#111827">b. If the bootloader is active, the Program Counter should be in system memory range.</span><br>
<span style="color:#111827">c. If the user application is active, the Program Counter should be in Flash range.</span><br>
<span style="color:#111827">d. The address ranges are described in the reference manual.</span><br>
<span style="color:#dc2626">※ This is stronger evidence than saying “the bootloader seems to run”</span><br>
<br>
<span style="color:#1d4ed8">8. Example interpretation</span><br>
<span style="color:#111827">a. BOOT0 high + required option bytes + reset = Program Counter in system memory.</span><br>
<span style="color:#111827">b. BOOT0 low + reset = Program Counter in user Flash.</span><br>
<span style="color:#111827">c. This confirms that boot mode selection is working.</span><br>
<span style="color:#111827">d. It also proves that the debugger can be used as an investigation tool.</span><br>
<span style="color:#dc2626">※ Verify boot mode by address range, not by assumption</span><br>
<br>
<span style="color:#1d4ed8">9. Key English sentence</span><br>
<span style="color:#111827">a. I verified bootloader activation by checking the Program Counter.</span><br>
<span style="color:#111827">b. When it was in system memory range, the embedded bootloader was active.</span><br>
<span style="color:#111827">c. When BOOT0 was low, the Program Counter moved to user Flash range after reset.</span><br>
<span style="color:#dc2626">※ Practice this sentence aloud</span><br>

## Page 4: Bootloader Communication Interfaces

<span style="color:#1d4ed8">10. Supported interfaces</span><br>
<span style="color:#111827">a. AN2606 lists supported bootloader interfaces for each STM32 device.</span><br>
<span style="color:#111827">b. For the example G4 device, supported interfaces include USART, I2C, SPI, and USB.</span><br>
<span style="color:#111827">c. Each interface has specific pins.</span><br>
<span style="color:#111827">d. The board design must route the expected pins correctly.</span><br>
<span style="color:#dc2626">※ If the pins are wrong, the bootloader may be active but unreachable</span><br>
<br>
<span style="color:#1d4ed8">11. First debugging advice</span><br>
<span style="color:#111827">a. If bootloader communication fails, first test the same hardware path.</span><br>
<span style="color:#111827">b. Create a simple user application for that interface.</span><br>
<span style="color:#111827">c. For example, test USART communication before blaming the bootloader.</span><br>
<span style="color:#111827">d. This checks board routing, connector, and pin correctness.</span><br>
<span style="color:#111827">e. It separates hardware-path problems from bootloader-state problems.</span><br>
<span style="color:#dc2626">※ Good debugging starts by isolating the failure domain</span><br>
<br>
<span style="color:#1d4ed8">12. Interface scanning behavior</span><br>
<span style="color:#111827">a. The embedded bootloader scans supported interfaces after activation.</span><br>
<span style="color:#111827">b. When it detects activity on one interface, it stops scanning other interfaces.</span><br>
<span style="color:#111827">c. Then it enters a loop waiting on the detected interface.</span><br>
<span style="color:#111827">d. This can block communication on the interface that the user actually wanted.</span><br>
<span style="color:#dc2626">※ This is the key lesson of the video</span><br>

## Page 5: Wrong Interface Detection Problem

<span style="color:#1d4ed8">13. Failure scenario</span><br>
<span style="color:#111827">a. The user wants to communicate with the bootloader through USART2.</span><br>
<span style="color:#111827">b. Before USART2 communication starts, another pin toggles.</span><br>
<span style="color:#111827">c. The bootloader interprets that activity as USART1 activity.</span><br>
<span style="color:#111827">d. The bootloader then waits on USART1.</span><br>
<span style="color:#111827">e. Communication through USART2 fails until the next reset.</span><br>
<span style="color:#dc2626">※ A random pin transition during power-up can select the wrong bootloader interface</span><br>
<br>
<span style="color:#1d4ed8">14. Why this matters in product design</span><br>
<span style="color:#111827">a. During board power-up, some external signals may toggle unexpectedly.</span><br>
<span style="color:#111827">b. If those pins are bootloader-supported interfaces, the bootloader may select the wrong interface.</span><br>
<span style="color:#111827">c. This can make production programming or field recovery unreliable.</span><br>
<span style="color:#111827">d. The embedded bootloader cannot be modified because it is provided by ST.</span><br>
<span style="color:#dc2626">※ Bootloader interface behavior must be considered during product definition</span><br>
<br>
<span style="color:#1d4ed8">15. Practical design implication</span><br>
<span style="color:#111827">a. Avoid unwanted activity on bootloader interface pins during reset and startup.</span><br>
<span style="color:#111827">b. Check pull-ups, pull-downs, external devices, and connector states.</span><br>
<span style="color:#111827">c. Keep the intended bootloader interface reachable and quiet until communication starts.</span><br>
<span style="color:#dc2626">※ Bootloader access is part of board-level design, not only firmware design</span><br>

## Page 6: Investigating Which Interface Was Activated

<span style="color:#1d4ed8">16. Investigation strategy</span><br>
<span style="color:#111827">a. If communication fails, identify which bootloader interface was initialized.</span><br>
<span style="color:#111827">b. Use AN2606 to list all possible bootloader interfaces.</span><br>
<span style="color:#111827">c. Use the reference manual to find each peripheral base address and register size.</span><br>
<span style="color:#111827">d. Dump peripheral register values through the debug link.</span><br>
<span style="color:#111827">e. Compare register values before and after communication attempts.</span><br>
<span style="color:#dc2626">※ This is register-level debugging of the bootloader state</span><br>
<br>
<span style="color:#1d4ed8">17. Why command line is useful</span><br>
<span style="color:#111827">a. The video recommends using STM32CubeProgrammer command line.</span><br>
<span style="color:#111827">b. The command line can dump register contents from several interfaces.</span><br>
<span style="color:#111827">c. This makes it easier to compare USART, I2C, SPI, and USB register states.</span><br>
<span style="color:#111827">d. The debug connection should not reset the board if the current bootloader state must be preserved.</span><br>
<span style="color:#dc2626">※ If you reset the board too early, you may destroy the evidence</span><br>
<br>
<span style="color:#1d4ed8">18. Evidence from register changes</span><br>
<span style="color:#111827">a. If USART2 was used, USART2 registers show communication-related changes.</span><br>
<span style="color:#111827">b. If a USART1 pin was toggled, USART1 registers show signs of attempted communication.</span><br>
<span style="color:#111827">c. If USB is plugged in, USB registers show connection activity.</span><br>
<span style="color:#111827">d. These changes reveal which interface the bootloader selected.</span><br>
<span style="color:#dc2626">※ The selected interface may not be the interface you expected</span><br>

## Page 7: Workarounds and Design Choices

<span style="color:#1d4ed8">19. Possible workaround 1</span><br>
<span style="color:#111827">a. Jump to the embedded bootloader from the user application.</span><br>
<span style="color:#111827">b. This allows the application to control when the bootloader is entered.</span><br>
<span style="color:#111827">c. It can also ensure that only the intended interface pins are active.</span><br>
<span style="color:#111827">d. This method is described in AN2606 for supported devices.</span><br>
<span style="color:#dc2626">※ This is not possible or identical on every STM32 chip</span><br>
<br>
<span style="color:#1d4ed8">20. Possible workaround 2</span><br>
<span style="color:#111827">a. Implement a custom bootloader.</span><br>
<span style="color:#111827">b. A custom bootloader can define exactly which interface and protocol to use.</span><br>
<span style="color:#111827">c. ST Cube firmware packages include bootloader examples for some devices.</span><br>
<span style="color:#111827">d. This gives more control but increases firmware complexity.</span><br>
<span style="color:#dc2626">※ Custom bootloader design must include safety, recovery, and update-failure handling</span><br>
<br>
<span style="color:#1d4ed8">21. Related protocol documents</span><br>
<span style="color:#111827">a. AN2606 explains system memory boot mode and activation patterns.</span><br>
<span style="color:#111827">b. Other ST application notes explain bootloader communication protocols.</span><br>
<span style="color:#111827">c. The relevant protocol document depends on the selected interface.</span><br>
<span style="color:#111827">d. USART, I2C, SPI, USB DFU, and CAN have different protocol details.</span><br>
<span style="color:#dc2626">※ Do not mix boot activation rules with communication protocol rules</span><br>

## Technical Vocabulary

<span style="color:#1d4ed8">embedded bootloader</span><br>
<span style="color:#111827">a. A built-in ST bootloader stored in system memory.</span><br>
<br>
<span style="color:#1d4ed8">activation pattern</span><br>
<span style="color:#111827">a. A required combination of pins and option bytes that makes the MCU boot into system memory.</span><br>
<br>
<span style="color:#1d4ed8">option byte</span><br>
<span style="color:#111827">a. A non-volatile configuration value that controls device behavior such as boot configuration or protection.</span><br>
<br>
<span style="color:#1d4ed8">Program Counter</span><br>
<span style="color:#111827">a. A CPU register that contains the address of the instruction currently being executed or about to be executed.</span><br>
<br>
<span style="color:#1d4ed8">system memory</span><br>
<span style="color:#111827">a. A protected memory area that contains the embedded bootloader.</span><br>
<br>
<span style="color:#1d4ed8">user Flash</span><br>
<span style="color:#111827">a. Flash memory where the user application firmware is stored.</span><br>
<br>
<span style="color:#1d4ed8">DFU</span><br>
<span style="color:#111827">a. Device Firmware Upgrade, commonly used for USB firmware update mode.</span><br>
<br>
<span style="color:#1d4ed8">register dump</span><br>
<span style="color:#111827">a. Reading raw peripheral register values to inspect hardware or firmware state.</span><br>

## 30-Second English Explanation

<span style="color:#1d4ed8">Interview answer</span><br>
<span style="color:#111827">a. STM32 MCUs include an embedded bootloader in system memory.</span><br>
<span style="color:#111827">b. To activate it correctly, I need to check the reference manual and AN2606.</span><br>
<span style="color:#111827">c. The required pin and option-byte pattern depends on the device.</span><br>
<span style="color:#111827">d. I can verify activation by checking whether the Program Counter is in system memory range.</span><br>
<span style="color:#111827">e. If communication fails, another interface may have been selected by unintended pin activity.</span><br>
<span style="color:#111827">f. In that case, I would dump peripheral registers to see which interface was initialized.</span><br>
<span style="color:#dc2626">※ Close with: bootloader debugging requires both firmware and board-level thinking</span><br>

## Practice Questions

<span style="color:#1d4ed8">Q1. Where is the STM32 embedded bootloader located?</span><br>
<span style="color:#111827">a. It is located in system memory inside the STM32 device.</span><br>
<br>
<span style="color:#1d4ed8">Q2. Which documents should be checked for bootloader activation?</span><br>
<span style="color:#111827">a. The MCU reference manual.</span><br>
<span style="color:#111827">b. AN2606.</span><br>
<span style="color:#111827">c. The board user manual.</span><br>
<br>
<span style="color:#1d4ed8">Q3. How can you verify that the bootloader is active?</span><br>
<span style="color:#111827">a. Check whether the Program Counter is in the system memory address range.</span><br>
<br>
<span style="color:#1d4ed8">Q4. Why can communication through the expected interface fail?</span><br>
<span style="color:#111827">a. Because the bootloader may have detected activity on another interface.</span><br>
<span style="color:#111827">b. After that, it stops scanning and waits on that interface.</span><br>
<br>
<span style="color:#1d4ed8">Q5. How can you investigate the selected interface?</span><br>
<span style="color:#111827">a. List possible interfaces from AN2606.</span><br>
<span style="color:#111827">b. Find register addresses in the reference manual.</span><br>
<span style="color:#111827">c. Dump the peripheral registers and compare values.</span><br>
<br>
<span style="color:#1d4ed8">Q6. Why is this important for product design?</span><br>
<span style="color:#111827">a. Because unintended pin activity during startup can select the wrong interface.</span><br>
<span style="color:#111827">b. This can make bootloader recovery or production programming unreliable.</span><br>

## Source

<span style="color:#1d4ed8">Original video</span><br>
<span style="color:#111827">STM32 boot and startup tips - Embedded bootloader investigations</span><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=kTMjjED8ErA">https://www.youtube.com/watch?v=kTMjjED8ErA</a><br>
<br>
<span style="color:#1d4ed8">Related document</span><br>
<span style="color:#111827">AN2606 - STM32 microcontroller system memory boot mode</span><br>
<span style="color:#dc2626">Use AN2606 to confirm activation patterns and available bootloader interfaces for each STM32 family.</span><br>
