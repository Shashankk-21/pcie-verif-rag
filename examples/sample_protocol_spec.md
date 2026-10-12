# Synthetic Ready/Valid Streaming Protocol

This is a synthetic educational example, not an official PCIe, AXI, or other vendor specification.

## Handshake and payload stability

A transfer occurs on a rising edge of `clk` when both `valid` and `ready` are high. The source must hold `valid` high until a transfer occurs. While `valid` is high and `ready` is low, the source must keep `payload` stable and must not withdraw the transaction.

## Reset behavior

When active-low `reset_n` is low, the source must drive `valid` low on the next rising edge. The sink must ignore transfers during reset. After reset is released, the source may present a transfer on the next rising edge.

## Boundaries and errors

The `length` signal is a 4-bit unsigned value and must be between 1 and 8 inclusive. A value outside this range is an error and must be reported with `error` high for one cycle. The source must not assert `valid` for an invalid length.

## Ordering

Transfers are observed by the sink in the same order they were accepted. No transfer may be duplicated or lost.
