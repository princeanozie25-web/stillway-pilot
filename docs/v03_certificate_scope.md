# v0.3 certificate: scope

This is about the any-length certificate of `stillway3/certify.py`. The Dispatch-2 certificate of v0.1 and its corrections are in `docs/v02_certificate_scope.md` and are unchanged.

## What is certified

For one checkpoint and one alphabet of leg kinds, with a clean result:

> In Dispatch-3, for every job of any number of legs built from leg kinds in the alphabet, every order, every state of the two gates and every event history, the route the planner's tables propose at every leg is one the exact planner allows, and every delivery goes to the dock the exact planner requires.

## Why it covers every length

A route decision depends on three things only: the two gate-requirement registers, the two gates, and the legs from the current one to the end. The reader turns the requirement registers into a code, then steps that code once per leg, from the last leg back to the leg after the current one. The exact planner does the same with a value table (for each of the four joint gate states, how many requirements can still be met).

The check runs both together. It starts from the 9 pairs of gate requirements and applies every leg kind to every (code, value table) pair found, until no new pair appears. There are at most 64 codes and 81 tables, so this ends. Any job, however long, only ever puts the reader in one of the pairs found. For each pair, each kind of current leg and each gate state, the proposed route is compared with the routes the value table allows.

## Bounds, all of them

| Dimension | Bound |
|---|---|
| World | Dispatch-3 only (`stillway3/world.py`, tested equal to the frozen `stillway2/world3.py` at 4 legs and to a plain-Python reference up to 10 legs). |
| Number of legs | Any. |
| Leg kinds | Alphabet "same": the 32 kinds whose two routes act on one gate. Alphabet "all": all 64. A result holds for its alphabet only. |
| Gates | Two. Every state. |
| Order | Every value of every field. Registers hold the order of record by rule; `tests/test_regcore.py` checks the rule under stress events. |
| Events | Any. Re-wiring, gate faults, bay closures, repaints and messages change the observation or a register, and a decision depends on nothing else. |
| Deliveries | 3 parcel values × 4 closed-bay states, all 12 checked. A parcel register that was never written is outside the check; it cannot occur after the first step of a job. |
| Waits and repaints | Not inputs of any learned function. |

## What the certificate is made on

Integer tables read off the network (`extract`): start (4×4), leg step (64×64), route (64×64×4), deliver (4×4). The tables are the certified object. They run as a planner without the network (`TablePlanner`).

The network is the same function as the tables up to floating-point ties. Two guards:

- `tests/test_regcore.py`: tables and network propose the same action at 10,828 action stages of sampled jobs, for every frozen discrete-carry core.
- Margins in each certificate: the smallest gap between the two nearest codes, and between the two routes where only one is valid. For certified imitation cores the route gap is 1.9 to 9.4.

The outcome-trained core `v3o_s1` has a clean certificate with a route gap of 0.87 where it matters, and a smallest code gap of 0.00005. Its tables are certified; its network sits close to a tie between two codes on some inputs and should be deployed as tables.

## What it needs

The rules of the world, in the form of the exact planner's value table. Training can do without planner labels (`v03/train_outcome.py`); certifying cannot do without the rules.

## What it does not cover

- Any world other than Dispatch-3, including more gates or other requirement types.
- Leg kinds outside the alphabet.
- The free-vector ablation cores (`v3c*`): no codes, no finite machine, no certificate.
- The v0.2 cores and arm M: their reader carries a free vector.
- Whether a wrong entry is ever reached by a realistic job mix. Three unclean cores made no error in 1.44 million sampled steps. The certificate reports that a failing job exists and gives one; it does not say how often such jobs arrive.

## How to check it without trusting the author

`python stillway3/check_tables.py results/v03/cert/<core>_tables.json all` needs only Python. It is a separate implementation: other data structures, its own exact planner, and a brute-force pass that lists every route choice of every job of up to 2 legs (alphabet all) or 3 legs (alphabet same) with no value table involved. The interactive page carries a third implementation in JavaScript; `node demo/test_proof.js` prints its counts.

Every unclean result comes with witness jobs in `results/v03/cert/<core>.json`, each replayed through the network in the simulator and compared with the plain-Python reference.
