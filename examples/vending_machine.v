// Vending Machine FSM
// Accepts 5 and 10 cent coins
// Dispenses item when 15 cents or more is inserted
// Returns change if necessary

module vending_machine(
    input clk,
    input reset,
    input coin_5,    // 5 cent coin inserted
    input coin_10,   // 10 cent coin inserted
    output dispense, // Dispense item
    output change_5  // Return 5 cent change
);

    // State encoding (3 bits for 6 states)
    reg [2:0] current_state;
    reg [2:0] next_state;
    
    // States represent amount collected
    parameter S0 = 3'b000;   // 0 cents
    parameter S5 = 3'b001;   // 5 cents
    parameter S10 = 3'b010;  // 10 cents
    parameter S15 = 3'b011;  // 15 cents (dispense)
    parameter S20 = 3'b100;  // 20 cents (dispense + change)
    
    // State register
    always @(posedge clk or posedge reset) begin
        if (reset)
            current_state <= S0;
        else
            current_state <= next_state;
    end
    
    // Next state logic
    always @(*) begin
        case (current_state)
            S0: begin
                if (coin_5)
                    next_state = S5;
                else if (coin_10)
                    next_state = S10;
                else
                    next_state = S0;
            end
            
            S5: begin
                if (coin_5)
                    next_state = S10;
                else if (coin_10)
                    next_state = S15;
                else
                    next_state = S5;
            end
            
            S10: begin
                if (coin_5)
                    next_state = S15;
                else if (coin_10)
                    next_state = S20;
                else
                    next_state = S10;
            end
            
            S15: begin
                next_state = S0;  // Dispense and reset
            end
            
            S20: begin
                next_state = S0;  // Dispense, give change, and reset
            end
            
            default: next_state = S0;
        endcase
    end
    
    // Output logic
    assign dispense = (current_state == S15) || (current_state == S20);
    assign change_5 = (current_state == S20);

endmodule
