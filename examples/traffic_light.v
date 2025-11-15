// Simple Traffic Light Controller FSM
// 4 states: RED, YELLOW, GREEN, RED_YELLOW
// 1 input: sensor (car detected)
// 3 outputs: red_light, yellow_light, green_light

module traffic_light_fsm(
    input clk,
    input reset,
    input sensor,
    output red_light,
    output yellow_light,
    output green_light
);

    // State encoding (2 bits for 4 states)
    reg [1:0] current_state;
    reg [1:0] next_state;
    
    // State definitions
    parameter RED = 2'b00;
    parameter YELLOW = 2'b01;
    parameter GREEN = 2'b10;
    parameter RED_YELLOW = 2'b11;
    
    // State register
    always @(posedge clk or posedge reset) begin
        if (reset)
            current_state <= RED;
        else
            current_state <= next_state;
    end
    
    // Next state logic
    always @(*) begin
        case (current_state)
            RED: begin
                if (sensor)
                    next_state = RED_YELLOW;
                else
                    next_state = RED;
            end
            
            RED_YELLOW: begin
                next_state = GREEN;
            end
            
            GREEN: begin
                if (!sensor)
                    next_state = YELLOW;
                else
                    next_state = GREEN;
            end
            
            YELLOW: begin
                next_state = RED;
            end
            
            default: next_state = RED;
        endcase
    end
    
    // Output logic
    assign red_light = (current_state == RED) || (current_state == RED_YELLOW);
    assign yellow_light = (current_state == YELLOW) || (current_state == RED_YELLOW);
    assign green_light = (current_state == GREEN);

endmodule
