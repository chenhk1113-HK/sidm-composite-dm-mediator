"""Derive Burkert V^2(r) closed form using sympy."""
import sympy as sp

r, rc, rho_c, rp = sp.symbols('r r_c rho_c r_p', positive=True)
# Burkert density
rho = rho_c * rc**3 / ((rp + rc) * (rp**2 + rc**2))
# Enclosed mass M(r) = int_0^r 4 pi rp^2 rho(rp) drp
M = sp.integrate(4 * sp.pi * rp**2 * rho, (rp, 0, r))
print('M(r) closed form:')
print(sp.simplify(M))
print()
# V^2(r) = G M(r) / r
V2 = M / r
print('V^2(r) closed form (simplified):')
V2_simplified = sp.simplify(V2)
print(V2_simplified)
print()
print('Numeric check at r=r_c, rho_c=1:')
val = V2_simplified.subs([(r, 1), (rc, 1), (rho_c, 1)])
print('V^2(r_c, rho_c=1) =', float(val))
print('Compare: 2*pi*G*rho_c*r_c^2*ln(2) would be', 2*3.14159265*4.302e-6*1*1*0.693147)