from pathlib import Path


def generate_approximate_adder(
    width: int,
    approx_bits: int,
    carry_truncation: int,
    correction_depth: int,
    output_file: str
):
    """
    Generate a parameterized approximate ripple-carry adder.

    Parameters
    ----------
    width : int
        Total adder width.

    approx_bits : int
        Number of least-significant bits operated approximately.

    carry_truncation : int
        Number of approximate stages where carry is forced to zero.

    correction_depth : int
        Number of lowest approximate stages restored to
        exact full-adder behavior.
    """

    if width <= 0:
        raise ValueError("Width must be positive.")

    if approx_bits < 0 or approx_bits > width:
        raise ValueError(
            "approx_bits must be between 0 and width."
        )

    if carry_truncation < 0 or carry_truncation > approx_bits:
        raise ValueError(
            "carry_truncation must be between 0 and approx_bits."
        )

    if correction_depth < 0:
        raise ValueError(
            "correction_depth cannot be negative."
        )

    if correction_depth > approx_bits:
        raise ValueError(
            "correction_depth cannot exceed approx_bits."
        )

    module_name = (
        f"approx_adder_w{width}"
        f"_k{approx_bits}"
        f"_t{carry_truncation}"
        f"_c{correction_depth}"
    )

    verilog = f"""\
`timescale 1ns/1ps

module {module_name} #(
    parameter WIDTH = {width},
    parameter APPROX_BITS = {approx_bits},
    parameter CARRY_TRUNC = {carry_truncation},
    parameter CORRECTION_DEPTH = {correction_depth}
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
"""

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        verilog,
        encoding="utf-8"
    )

    return output_path