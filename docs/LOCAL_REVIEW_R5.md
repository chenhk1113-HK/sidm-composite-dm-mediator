# Local Review (Reviewer 1, Round 5)

**Model:** `Qwen3.6-35B-A3B-UD-Q4_K_M` (local llama.cpp on 127.0.0.1:50113)  
**Generated:** 2026-10-22 12:45:26  
**Transport:** direct local OpenAI-compatible `/v1/chat/completions`  
**Why local:** OpenRouter free tier is account-blocked for this host today (HTTP 429 `free-models-per-day` on every free model, including the delegated Nemotron 3 Ultra 550B).  
**Reviewer role:** second independent reviewer, different model family from the OpenCode-side reviewer (DeepSeek/GLM/MiMo).  
**Excerpt source:** `R5_EXCERPT.md` (36199 chars, inlined — the local endpoint has no tool support).  

> **Status: UNVERIFIED SECOND OPINION.** Every specific numerical claim below must be recomputed in Python before it is acted on.

## Review

[ERR] F3 (L117): The computed Gaussian tail value is incorrect.
Formula: $\exp[-(15-29.4)^2/(2 \cdot 3.0^2)]$
Calculation:
Numerator: $(15 - 29.4)^2 = (-14.4)^2 = 207.36$
Denominator: $2 \cdot 3.0^2 = 2 \cdot 9 = 18$
Exponent: $-207.36 / 18 = -11.52$
Result: $e^{-11.52} \approx 1.00 \times 10^{-5}$.
The paper states "1.0×10⁻⁵". This is **correct**.
*Correction*: The prompt asks to verify if it is right. It is right.
Status: [OK]

[ERR] F6 (L82): The computed resonance velocity is incorrect.
Formula: $v_{res} = c \cdot \sqrt{8 \cdot \Delta M / (2 m_\chi)}$
Given: $\Delta M / (2 m_\chi) = 1.2 \times 10^{-9}$.
Calculation:
Inside sqrt: $8 \cdot 1.2 \times 10^{-9} = 9.6 \times 10^{-9}$.
Sqrt: $\sqrt{9.6 \times 10^{-9}} \approx 9.798 \times 10^{-5}$.
The paper claims this gives 29.4 km/s.
If $v_{res} = 29.4$ km/s, then $c = 29.4 / (9.798 \times 10^{-5}) \approx 300,000$ km/s, which is $c$ (speed of light).
However, the formula in L82 is $v_{res} = c \cdot \sqrt{\dots}$. In standard kinematics, $E = \frac{1}{2} m v^2$. For s-channel resonance at $\sqrt{s} = 2m + \Delta M$, $\frac{1}{2} m v^2 = \Delta M \implies v = \sqrt{2 \Delta M / m}$.
The formula in L82 uses $2 m_\chi$ in the denominator, implying $\sqrt{s} \approx 2 m_\chi$.
$v = \sqrt{2 \Delta M / m_\chi} = \sqrt{4 \Delta M / (2 m_\chi)} = 2 \sqrt{\Delta M / (2 m_\chi)}$.
The paper's formula has $\sqrt{8 \dots} = \sqrt{4 \cdot 2 \dots} = 2 \sqrt{2 \dots}$.
Let's check the factor.
Standard: $v = \sqrt{2 \Delta M / m_\chi}$.
Paper: $v = c \sqrt{8 \Delta M / (2 m_\chi)} = c \sqrt{4 \Delta M / m_\chi} = 2c \sqrt{\Delta M / m_\chi}$.
This is dimensionally inconsistent if $c$ is just a constant, unless $c$ carries units.
If $c=1$ (natural units), $v = \sqrt{4 \Delta M / m_\chi}$.
$\Delta M / m_\chi = 2 \cdot 1.2 \times 10^{-9} = 2.4 \times 10^{-9}$.
$v = \sqrt{4 \cdot 2.4 \times 10^{-9}} = \sqrt{9.6 \times 10^{-9}} \approx 9.8 \times 10^{-5}$ (in units of $c$).
$9.8 \times 10^{-5} \cdot 300,000 \text{ km/s} \approx 29.4$ km/s.
So the formula $v = c \sqrt{8 \Delta M / (2 m_\chi)}$ works IF $c$ is the speed of light and the term under sqrt is dimensionless ratio $\Delta M / m_\chi$? No, $\Delta M / (2 m_\chi)$ is dimensionless.
Wait, $\sqrt{8 \cdot 1.2e-9} \approx 9.8e-5$.
$9.8e-5 \cdot c \approx 29.4$ km/s.
This implies the formula is effectively $v = c \sqrt{4 \Delta M / m_\chi}$?
Standard non-relativistic: $E_{cm} = 2 m_\chi + \frac{1}{2} (2 m_\chi) v_{rel}^2 / 4$? No.
$\sqrt{s} = 2 \sqrt{m_\chi^2 + p^2} \approx 2 m_\chi + p^2/m_\chi$.
$p = m_\chi v_{rel} / 2$? No, $p = \mu v_{rel} = (m_\chi/2) v_{rel}$.
$\sqrt{s} \approx 2 m_\chi + \frac{(m_\chi/2 v_{rel})^2}{m_\chi} = 2 m_\chi + \frac{1}{4} m_\chi v_{rel}^2$.
Set $\sqrt{s} = 2 m_\chi + \Delta M$.
$\Delta M = \frac{1}{4} m_\chi v_{rel}^2 \implies v_{rel} = \sqrt{4 \Delta M / m_\chi} = 2 \sqrt{\Delta M / m_\chi}$.
Paper formula: $c \sqrt{8 \Delta M / (2 m_\chi)} = c \sqrt{4 \Delta M / m_\chi} = 2 c \sqrt{\Delta M / m_\chi}$.
If $c=1$ (speed of light in km/s), this matches.
So the formula is correct *if* $c$ is interpreted as the speed of light constant.
However, L82 writes $v_{res} = c \cdot \sqrt{\dots}$. Usually $c$ is a parameter.
The computation $\sqrt{8 \cdot 1.2e-9} \approx 9.8e-5$.
$9.8e-5 \cdot 300,000 = 29.4$.
So the number 29.4 is correct based on the inputs.
Status: [OK]

[ERR] F8 (L189-190): The cap calculation is incorrect.
Given: Ratio $K / \sigma_{peak}$.
At $\sigma_{peak} = 50$, Ratio $= 2.86$.
So $K = 2.86 \cdot 50 = 143$.
Cap is where Ratio $= 3.0$.
$3.0 = 143 / \sigma_{cap} \implies \sigma_{cap} = 143 / 3.0 = 47.666...$
Paper states 47.67.
This is correct.
Status: [OK]

[ERR] F11 (L189-190): The floor calculation is incorrect.
Formula: Floor requires $\sigma/m(28) \ge 50$.
$\sigma/m(28) \approx \sigma_{peak} \cdot \text{Gaussian}(28) + \text{Background}$.
Gaussian at 28: $\exp(-(28-29.4)^2 / (2 \cdot 4.4^2)) = \exp(-1.96 / 38.72) = \exp(-0.0506) \approx 0.9506$.
Background at 28: $0.052 \cdot (100/28)^{1.93} \approx 0.052 \cdot 3.28 \approx 0.17$.
Total $\sigma/m(28) \approx 0.9506 \sigma_{peak} + 0.17$.
Set $\ge 50$:
$0.9506 \sigma_{peak} \ge 49.83 \implies \sigma_{peak} \ge 49.83 / 0.9506 \approx 52.42$.
Paper states floor is 51.96.
Let's check if they used a different background or width.
If $\sigma_1 = 4.4$, $w=4.4$.
Maybe they used $\sigma/m(28) = \sigma_{peak}$? No, that would be 50.
Maybe they used the Breit-W

---
**Duration:** 102.3s  
**Usage:** {'completion_tokens': 2000, 'prompt_tokens': 14252, 'total_tokens': 16252, 'prompt_tokens_details': {'cached_tokens': 0}}
