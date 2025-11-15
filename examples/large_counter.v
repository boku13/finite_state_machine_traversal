// Large Counter FSM with 64 States
// 6-bit counter demonstrating complex FSM traversal
// Supports count up, count down, and reset operations

module large_counter(
    input clk,
    input reset,
    input enable,      // 1 = count, 0 = pause
    input direction,   // 1 = count up, 0 = count down
    output [5:0] count,
    output max_count,
    output min_count
);

    // State encoding: 6-bit counter (64 states: 0 to 63)
    reg [5:0] current_state;
    reg [5:0] next_state;
    
    // State parameters for readability
    parameter MIN = 6'b000000;  // 0
    parameter MAX = 6'b111111;  // 63
    
    // State register (sequential logic)
    always @(posedge clk or posedge reset) begin
        if (reset)
            current_state <= MIN;
        else
            current_state <= next_state;
    end
    
    // Next state logic (combinational logic)
    always @(*) begin
        if (!enable) begin
            // Pause - stay in current state
            next_state = current_state;
        end else if (direction) begin
            // Count up
            if (current_state == MAX)
                next_state = MIN;  // Wrap around
            else
                next_state = current_state + 6'b000001;
        end else begin
            // Count down
            if (current_state == MIN)
                next_state = MAX;  // Wrap around
            else
                next_state = current_state - 6'b000001;
        end
    end
    
    // Output logic
    assign count = current_state;
    assign max_count = (current_state == MAX);
    assign min_count = (current_state == MIN);

endmodule
