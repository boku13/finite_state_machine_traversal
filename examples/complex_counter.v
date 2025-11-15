// Complex Counter-based FSM
// 8-bit counter with multiple modes
// Can count up, down, load, and pause
// Demonstrates a larger state space (256 states)

module complex_counter(
    input clk,
    input reset,
    input [1:0] mode,  // 00=pause, 01=count up, 10=count down, 11=load
    input [7:0] load_value,
    output [7:0] count,
    output overflow,
    output underflow
);

    // 8-bit state register
    reg [7:0] current_state;
    reg [7:0] next_state;
    
    // State register
    always @(posedge clk or posedge reset) begin
        if (reset)
            current_state <= 8'h00;
        else
            current_state <= next_state;
    end
    
    // Next state logic
    always @(*) begin
        case (mode)
            2'b00: next_state = current_state;           // Pause
            2'b01: next_state = current_state + 8'h01;   // Count up
            2'b10: next_state = current_state - 8'h01;   // Count down
            2'b11: next_state = load_value;              // Load
            default: next_state = current_state;
        endcase
    end
    
    // Output logic
    assign count = current_state;
    assign overflow = (mode == 2'b01) && (current_state == 8'hFF);
    assign underflow = (mode == 2'b10) && (current_state == 8'h00);

endmodule
