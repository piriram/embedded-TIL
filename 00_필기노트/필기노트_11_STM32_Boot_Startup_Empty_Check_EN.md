# Ch.11 STM32 Boot and Startup - Empty Check Mechanism

Purpose: English handwritten-note version after Ch.10

Rules:

- Focus on technical English expressions
- Keep each sentence short enough to speak aloud
- Blue: title, section number, key term
- Black: explanation and example
- Red: warning, interview caution, common mistake
- Use this note to practice both embedded concepts and English explanation

## Page 1: What Is the Empty Check Mechanism?

<span style="color:#1d4ed8">Topic: STM32 Empty Check Mechanism</span><br>
<span style="color:#1d4ed8">1. Core idea</span><br>
<span style="color:#111827">The empty check mechanism is a boot behavior on some STM32 microcontrollers.</span><br>
<span style="color:#111827">If the first address in Flash is empty, the MCU boots into the system bootloader.</span><br>
<span style="color:#111827">This helps program a blank device without changing the BOOT pins.</span><br>
<span style="color:#111827">It is useful for virgin devices during first programming.</span><br>
<span style="color:#dc2626">Warning: helpful for programming, but dangerous if the board is already assembled.</span><br>
<br>
<span style="color:#1d4ed8">2. Key boot paths</span><br>
<span style="color:#111827">Normal case: Flash has user firmware → MCU executes user application.</span><br>
<span style="color:#111827">Empty case: Flash looks empty → MCU enters system memory bootloader.</span><br>
<span style="color:#111827">The system bootloader is built into the STM32 device.</span><br>
<span style="color:#111827">It allows programming through supported interfaces such as UART or other bootloader interfaces.</span><br>
<span style="color:#dc2626">Do not confuse system bootloader with user application boot code.</span><br>
<br>
<span style="color:#1d4ed8">3. Why ST added this mechanism</span><br>
<span style="color:#111827">A blank MCU needs a way to receive firmware.</span><br>
<span style="color:#111827">Without empty check, the user may need to force BOOT pins to a specific level.</span><br>
<span style="color:#111827">With empty check, the MCU can automatically enter the system bootloader.</span><br>
<span style="color:#111827">This simplifies first-time programming in production or prototyping.</span><br>
<span style="color:#dc2626">Interview point: explain both the benefit and the risk.</span><br>

## Page 2: Why Can It Cause Problems?

<span style="color:#1d4ed8">4. GPIO side effect</span><br>
<span style="color:#111827">When the system bootloader runs, it may configure several GPIO pins as outputs.</span><br>
<span style="color:#111827">Those pins may be connected to external circuits on an assembled PCB.</span><br>
<span style="color:#111827">If an output pin is tied directly to GND or VDD, it can create a short circuit.</span><br>
<span style="color:#111827">In the worst case, this can damage the microcontroller or external components.</span><br>
<span style="color:#dc2626">Important: boot behavior is also a hardware safety issue.</span><br>
<br>
<span style="color:#1d4ed8">5. Reset after programming issue</span><br>
<span style="color:#111827">After programming, the Flash is no longer empty.</span><br>
<span style="color:#111827">However, the MCU may still boot into the system bootloader after reset.</span><br>
<span style="color:#111827">This happens because the empty check bit still needs to be cleared.</span><br>
<span style="color:#111827">A simple reset through the reset pin may not be enough.</span><br>
<span style="color:#dc2626">Common mistake: assuming that flashing code automatically clears the empty check condition.</span><br>
<br>
<span style="color:#1d4ed8">6. STM32 families mentioned</span><br>
<span style="color:#111827">The mechanism is present on all STM32G0 and STM32WB part numbers.</span><br>
<span style="color:#111827">It is also present on some STM32L0, STM32L4, and STM32F0 devices.</span><br>
<span style="color:#111827">Always check the reference manual and bootloader application note for the exact device.</span><br>
<span style="color:#111827">The video points to AN2606 for STM32 system memory boot mode.</span><br>
<span style="color:#dc2626">Do not generalize one STM32 family behavior to every STM32 device.</span><br>

## Page 3: Safe Programming Procedure

<span style="color:#1d4ed8">7. Goal of the procedure</span><br>
<span style="color:#111827">The goal is to program an empty STM32 without letting the system bootloader run.</span><br>
<span style="color:#111827">This is useful when the MCU is already soldered on a PCB.</span><br>
<span style="color:#111827">The procedure reduces the risk of unwanted GPIO output states.</span><br>
<span style="color:#dc2626">The main idea is to keep the MCU under reset while connecting the debugger.</span><br>
<br>
<span style="color:#1d4ed8">8. Step-by-step flow</span><br>
<span style="color:#111827">Step 1: Keep the MCU under reset before and after applying power.</span><br>
<span style="color:#111827">Step 2: GPIO pins stay in analog or high-impedance mode, except debug pins.</span><br>
<span style="color:#111827">Step 3: Connect the debugger using connect under reset.</span><br>
<span style="color:#111827">Step 4: Hold the core before it executes any instruction.</span><br>
<span style="color:#111827">Step 5: Program the Flash with the user application.</span><br>
<span style="color:#111827">Step 6: Clear the empty check bit before the next normal boot.</span><br>
<span style="color:#dc2626">If the empty check bit is not cleared, the MCU may boot into system memory again.</span><br>
<br>
<span style="color:#1d4ed8">9. Ways to clear the empty check bit</span><br>
<span style="color:#111827">Option 1: Power-cycle the board.</span><br>
<span style="color:#111827">Option 2: Perform option byte launch.</span><br>
<span style="color:#111827">Option 3: Clear the empty bit directly in the Flash configuration register.</span><br>
<span style="color:#111827">The direct register method is available only on STM32G0 and STM32WB.</span><br>
<span style="color:#dc2626">Power cycling may not be possible if the battery is already assembled.</span><br>

## Page 4: CubeProgrammer Hands-On Summary

<span style="color:#1d4ed8">10. Demo setup</span><br>
<span style="color:#111827">The demo uses an STM32G0 Nucleo board with empty internal Flash.</span><br>
<span style="color:#111827">An external yellow LED is connected to PA9.</span><br>
<span style="color:#111827">PA9 is used as UART1 transmit by the system bootloader.</span><br>
<span style="color:#111827">If the bootloader runs, PA9 becomes output and the yellow LED turns on.</span><br>
<span style="color:#111827">The user application simply blinks the green LED on the Nucleo board.</span><br>
<br>
<span style="color:#1d4ed8">11. CubeProgrammer sequence</span><br>
<span style="color:#111827">Open STM32CubeProgrammer.</span><br>
<span style="color:#111827">Select ST-LINK mode.</span><br>
<span style="color:#111827">Choose connect under reset instead of normal or hot plug.</span><br>
<span style="color:#111827">Hold the physical reset button and connect with ST-LINK.</span><br>
<span style="color:#111827">Release reset after the debugger connects.</span><br>
<span style="color:#111827">Program the application hex file.</span><br>
<span style="color:#111827">Trigger option byte launch to clear the empty check condition.</span><br>
<span style="color:#111827">Disconnect and verify that the user application runs.</span><br>
<span style="color:#dc2626">Key evidence: yellow LED stays off, green LED blinks.</span><br>
<br>
<span style="color:#1d4ed8">12. What the demo proves</span><br>
<span style="color:#111827">The MCU can be programmed while the bootloader is prevented from executing.</span><br>
<span style="color:#111827">Connect under reset gives debugger control before user or bootloader code runs.</span><br>
<span style="color:#111827">Option byte launch makes the MCU resample the empty check state.</span><br>
<span style="color:#111827">After the empty check condition is cleared, the MCU boots into user Flash.</span><br>
<span style="color:#dc2626">This is a practical production-programming concept, not just theory.</span><br>

## Technical Vocabulary

<span style="color:#1d4ed8">empty check mechanism</span><br>
<span style="color:#111827">A hardware or boot-time mechanism that checks whether the first Flash address is empty.</span><br>
<br>
<span style="color:#1d4ed8">system bootloader</span><br>
<span style="color:#111827">A built-in bootloader stored in system memory by ST.</span><br>
<br>
<span style="color:#1d4ed8">virgin device</span><br>
<span style="color:#111827">A new MCU that has not been programmed yet.</span><br>
<br>
<span style="color:#1d4ed8">assembled PCB</span><br>
<span style="color:#111827">A printed circuit board where components are already mounted.</span><br>
<br>
<span style="color:#1d4ed8">connect under reset</span><br>
<span style="color:#111827">A debug connection mode where the debugger connects while the MCU is held in reset.</span><br>
<br>
<span style="color:#1d4ed8">option byte launch</span><br>
<span style="color:#111827">A procedure that reloads option byte settings and causes a system reset.</span><br>
<br>
<span style="color:#1d4ed8">high impedance</span><br>
<span style="color:#111827">A pin state where the pin does not strongly drive high or low.</span><br>

## 30-Second English Explanation

<span style="color:#1d4ed8">Interview answer</span><br>
<span style="color:#111827">The empty check mechanism on some STM32 devices checks whether the first address in Flash is empty.</span><br>
<span style="color:#111827">If it is empty, the MCU boots into the built-in system bootloader instead of user Flash.</span><br>
<span style="color:#111827">This is useful for programming a blank device, but it can be risky on an assembled PCB because the bootloader may configure some GPIOs as outputs.</span><br>
<span style="color:#111827">To avoid this, the MCU can be programmed by connecting the debugger under reset, flashing the application, and then clearing the empty check condition through power cycling or option byte launch.</span><br>
<span style="color:#dc2626">Close with: I understand this as both a boot-flow issue and a board-safety issue.</span><br>

## Practice Questions

<span style="color:#1d4ed8">Q1. Why does a blank STM32 boot into system memory?</span><br>
<span style="color:#111827">Because the empty check mechanism detects that the first Flash address is empty.</span><br>
<br>
<span style="color:#1d4ed8">Q2. Why can this be dangerous on an assembled PCB?</span><br>
<span style="color:#111827">Because the system bootloader may configure GPIOs as outputs, and those pins may be connected to external circuits.</span><br>
<br>
<span style="color:#1d4ed8">Q3. What does connect under reset mean?</span><br>
<span style="color:#111827">It means the debugger connects while the MCU is held in reset, before the core executes instructions.</span><br>
<br>
<span style="color:#1d4ed8">Q4. Why is programming alone not always enough?</span><br>
<span style="color:#111827">Because the empty check bit may still need to be cleared before the next reset.</span><br>
<br>
<span style="color:#1d4ed8">Q5. Which document should be checked for STM32 bootloader behavior?</span><br>
<span style="color:#111827">AN2606, the STM32 system memory boot mode application note.</span><br>

## Source

<span style="color:#1d4ed8">Original video</span><br>
<span style="color:#111827">STM32 boot and startup tips - Empty check mechanism</span><br>
<a style="color:#111827" href="https://www.youtube.com/watch?v=mBU9xHqw264">https://www.youtube.com/watch?v=mBU9xHqw264</a><br>
<br>
<span style="color:#1d4ed8">Related document</span><br>
<span style="color:#111827">AN2606 - STM32 microcontroller system memory boot mode</span><br>
<span style="color:#dc2626">Use the application note to verify exact bootloader behavior for each STM32 family.</span><br>
