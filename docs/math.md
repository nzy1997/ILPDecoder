# ILP Model for QEC Decoding

This page summarizes the integer linear program (ILP) used by ILPQEC.

## Notation

- Parity-check matrix: $H \in \{0,1\}^{m \times n}$
- Syndrome: $s \in \{0,1\}^m$
- Error variables: $e \in \{0,1\}^n$
- Weights: $w \in \mathbb{R}^n$

Each column of `H` corresponds to an error mechanism, and each row corresponds
to a detector or parity check.

## Maximum-Likelihood ILP

The decoding problem is:

$$
\min_{e} \sum_{j=0}^{n-1} w_j e_j
$$

subject to the parity constraints:

$$
H e \equiv s \pmod{2}, \quad e \in \{0,1\}^n.
$$

To express parity over the integers, introduce auxiliary variables
$a \in \mathbb{Z}_{\ge 0}^m$ and write:

$$
H e - 2 a = s.
$$

The full ILP is:

$$
\begin{aligned}
\min_{e, a} \quad & \sum_{j=0}^{n-1} w_j e_j \\
\text{s.t.} \quad & H e - 2 a = s \\
& e \in \{0,1\}^n, \; a \in \mathbb{Z}_{\ge 0}^m.
\end{aligned}
$$

## Weights from Error Probabilities

If each error mechanism has an independent probability $p_j$, the standard
log-likelihood ratio weight is:

$$
w_j = \log\left(\frac{1 - p_j}{p_j}\right).
$$

Minimizing the weighted sum is equivalent to maximum-likelihood decoding
under the independent error model. ILPQEC requires $p_j \in (0, 0.5]$ and
rejects larger values; provide explicit weights if $p_j > 0.5$.

## Observables (Stim DEM)

When decoding a Stim DetectorErrorModel, the DEM is parsed into:

- `H`: detector parity-check matrix
- `O`: observable matrix
- `w`: weights derived from `error(p)` lines

After solving for `e`, the predicted logical observables are:

$$
\text{obs} = (O e) \bmod 2.
$$

## Assumptions

- Error mechanisms are treated as independent.
- Probabilities are mapped to weights as above.
- For DEM specifics (supported instructions, `^` handling, flattening), see
  `stim_dem.md`.
