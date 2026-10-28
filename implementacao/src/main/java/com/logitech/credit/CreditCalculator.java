package com.logitech.credit;

public class CreditCalculator {

    public static double calculate(CustomerType customerType, double freightValue, double delayHours) {
        if (customerType == CustomerType.COURTESY) {
            return 0.0;
        }

        if (delayHours <= 2.0) {
            return 0.0;
        }

        double percentage;
        if (customerType == CustomerType.CORPORATE) {
            if (delayHours <= 24.0) {
                percentage = 0.20;
            } else if (delayHours <= 72.0) {
                percentage = 0.50;
            } else {
                percentage = 1.0;
            }
        } else {
            if (delayHours <= 24.0) {
                percentage = 0.10;
            } else if (delayHours <= 72.0) {
                percentage = 0.25;
            } else {
                percentage = 0.50;
            }
        }

        double credit = freightValue * percentage;
        double maxCredit = customerType == CustomerType.CORPORATE ? 2000.0 : 500.0;
        return Math.min(credit, maxCredit);
    }
}
