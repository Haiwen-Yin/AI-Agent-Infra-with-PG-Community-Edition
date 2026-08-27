-- v4.4.10 external Agent Embedding execution declaration and Contract evidence.
ALTER TABLE agent_registrations ADD COLUMN IF NOT EXISTS embedding_mode varchar(24) NOT NULL DEFAULT 'PLATFORM_MANAGED';
ALTER TABLE agent_registrations ADD COLUMN IF NOT EXISTS embedding_model_id varchar(256);
ALTER TABLE agent_registrations ADD COLUMN IF NOT EXISTS embedding_fingerprint varchar(256);
ALTER TABLE agent_registrations ADD COLUMN IF NOT EXISTS embedding_dimension integer;
ALTER TABLE agent_registrations ADD COLUMN IF NOT EXISTS embedding_distance_metric varchar(32) NOT NULL DEFAULT 'COSINE';
ALTER TABLE agent_registrations ADD COLUMN IF NOT EXISTS embedding_normalize char(1) NOT NULL DEFAULT 'Y';
