`timescale 1ns/1ps

module test_approx_adder;

    reg [15:0] a;
    reg [15:0] b;
    reg        cin;

    wire [15:0] sum;
    wire        cout;

    integer i;
    integer exact_result;
    integer approx_result;
    integer error;

    integer error_count;
    integer total_error;
    integer max_error;

    // --------------------------------------------------------
    // Device Under Test
    // --------------------------------------------------------

    approx_adder_w16_k4_t2_c1 dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    // --------------------------------------------------------
    // Simulation
    // --------------------------------------------------------

    initial begin

        error_count = 0;
        total_error = 0;
        max_error = 0;

        cin = 0;

        // ----------------------------------------------------
        // Deterministic test vectors
        // ----------------------------------------------------

        for (i = 0; i < 1000; i = i + 1) begin

            a = (i * 37) % 65536;
            b = (i * 91) % 65536;

            #1;

            exact_result = a + b;
            approx_result = {cout, sum};

            error = exact_result - approx_result;

            if (error < 0)
                error = -error;

            if (error != 0)
                error_count = error_count + 1;

            total_error = total_error + error;

            if (error > max_error)
                max_error = error;

        end

        // ----------------------------------------------------
        // Results
        // ----------------------------------------------------

        $display("==============================================");
        $display("AUTOMATED APPROXIMATE ADDER CHARACTERIZATION");
        $display("==============================================");

        $display("Number of vectors : %0d", 1000);
        $display("Error vectors     : %0d", error_count);
        $display("Total error       : %0d", total_error);
        $display("Maximum error     : %0d", max_error);

        $display("==============================================");

        $finish;

    end

endmodule