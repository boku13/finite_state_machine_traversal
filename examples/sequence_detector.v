// Simple 2-bit sequence detector (gate-level description)
// Detects sequence "11" in the input stream
// State encoding: 2 bits (00 = IDLE, 01 = GOT_1, 10 = GOT_11)

module sequence_detector_gate(
    input clk,
    input reset,
    input x,
    output detected
);

    // State registers
    wire state0, state1;
    wire next_state0, next_state1;
    
    // D flip-flops for state storage
    dff dff0(.clk(clk), .reset(reset), .d(next_state0), .q(state0));
    dff dff1(.clk(clk), .reset(reset), .d(next_state1), .q(state1));
    
    // Next state logic (gate-level)
    // next_state0 = x AND NOT(state0) AND NOT(state1)  OR  x AND state0 AND NOT(state1)
    wire w1, w2, w3, w4, w5, w6;
    not n0(w1, state0);
    not n1(w2, state1);
    and a0(w3, x, w1, w2);
    and a1(w4, x, state0, w2);
    or o0(next_state0, w3, w4);
    
    // next_state1 = x AND state0 AND NOT(state1)
    and a2(next_state1, x, state0, w2);
    
    // Output logic: detected = state1
    buf b0(detected, state1);

endmodule

// D Flip-Flop module
module dff(
    input clk,
    input reset,
    input d,
    output reg q
);
    always @(posedge clk or posedge reset) begin
        if (reset)
            q <= 1'b0;
        else
            q <= d;
    end
endmodule
