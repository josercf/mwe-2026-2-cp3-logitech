package com.logitech.credit;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CreditCalculatorTest {

    @Test
    void shouldReturnZeroWhenBelowTolerance() {
        assertEquals(0.0, CreditCalculator.calculate(CustomerType.RETAIL, 300.0, 1.59), 0.001);
    }

    @Test
    void shouldCalculateRetailCreditAtTwoHours() {
        assertEquals(30.0, CreditCalculator.calculate(CustomerType.RETAIL, 300.0, 2.01), 0.001);
    }

    @Test
    void shouldDoubleCorporatePercentages() {
        assertEquals(200.0, CreditCalculator.calculate(CustomerType.CORPORATE, 1000.0, 3.0), 0.001);
    }

    @Test
    void shouldApplyRetailCap() {
        assertEquals(500.0, CreditCalculator.calculate(CustomerType.RETAIL, 10000.0, 120.0), 0.001);
    }

    @Test
    void shouldReturnZeroForCourtesy() {
        assertEquals(0.0, CreditCalculator.calculate(CustomerType.COURTESY, 0.0, 30.0), 0.001);
    }
}
