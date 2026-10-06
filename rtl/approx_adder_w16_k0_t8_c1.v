`timescale 1ns/1ps

module approx_adder_w16_k0_t8_c1 #(
    parameter WIDTH = 16,
    parameter APPROX_BITS = 0,
    parameter CARRY_TRUNC = 8,
    parameter CORRECTION_DEPTH = 1
)(
    input  wire [WIDTH-1:0] a,
    input  wire [WIDTH-1:0] b,
    input  wire             cin,
    output wire [WIDTH-1:0] sum,
    output wire             cout
);

    wire [WIDTH:0] carry;

    assign carry[0] = cin;

    genvar i;

    generate

        for (i = 0; i < WIDTH; i = i + 1) begin : ADDER

            if (i < APPROX_BITS) begin

                /*
                 * Approximate region
                 */

                assign sum[i] = a[i] ^ b[i];

                if (i < CARRY_TRUNC) begin

                    assign carry[i+1] = 1'b0;

                end
                else begin

                    assign carry[i+1] =
                        a[i] & b[i];

                end

            end
            else begin

                /*
                 * Accurate region
                 */

                assign sum[i] =
                    a[i] ^
                    b[i] ^
                    carry[i];

                assign carry[i+1] =
                    (a[i] & b[i]) |
                    (a[i] & carry[i]) |
                    (b[i] & carry[i]);

            end

        end

    endgenerate

    assign cout = carry[WIDTH];

endmodule
