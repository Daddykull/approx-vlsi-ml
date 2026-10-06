`timescale 1ns/1ps

module approx_adder_w16_k6_t0_c2 #(
    parameter WIDTH = 16,
    parameter APPROX_BITS = 6,
    parameter CARRY_TRUNC = 0,
    parameter CORRECTION_DEPTH = 2
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

            /*
             * Exact region
             *
             * Bits above APPROX_BITS use normal
             * full-adder logic.
             */
            if (i >= APPROX_BITS) begin

                assign sum[i] =
                    a[i] ^
                    b[i] ^
                    carry[i];

                assign carry[i+1] =
                    (a[i] & b[i]) |
                    (a[i] & carry[i]) |
                    (b[i] & carry[i]);

            end

            /*
             * Corrected approximate region
             *
             * The lowest CORRECTION_DEPTH approximate
             * stages are restored to exact behavior.
             */
            else if (i < CORRECTION_DEPTH) begin

                assign sum[i] =
                    a[i] ^
                    b[i] ^
                    carry[i];

                assign carry[i+1] =
                    (a[i] & b[i]) |
                    (a[i] & carry[i]) |
                    (b[i] & carry[i]);

            end

            /*
             * Remaining approximate region
             */
            else begin

                assign sum[i] =
                    a[i] ^
                    b[i];

                if (i < CARRY_TRUNC) begin

                    assign carry[i+1] = 1'b0;

                end
                else begin

                    assign carry[i+1] =
                        a[i] & b[i];

                end

            end

        end

    endgenerate

    assign cout = carry[WIDTH];

endmodule
