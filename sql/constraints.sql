-- SQL constraints definitions
-- Detail reference mapping for table constraints and business rules

-- fact_transactions transaction_type constraint
-- CHECK (transaction_type IN ('Sip', 'Lumpsum', 'Redemption'))

-- fact_transactions kyc_status constraint
-- CHECK (kyc_status IN ('Verified', 'Pending'))

-- fact_performance rating range constraint
-- CHECK (morningstar_rating >= 1 AND morningstar_rating <= 5)
