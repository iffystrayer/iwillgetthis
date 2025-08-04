--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: assessmentstatus; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.assessmentstatus AS ENUM (
    'DRAFT',
    'IN_PROGRESS',
    'UNDER_REVIEW',
    'COMPLETED',
    'ARCHIVED'
);


ALTER TYPE public.assessmentstatus OWNER TO aegis_user;

--
-- Name: assetcriticality; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.assetcriticality AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);


ALTER TYPE public.assetcriticality OWNER TO aegis_user;

--
-- Name: assettype; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.assettype AS ENUM (
    'SERVER',
    'WORKSTATION',
    'NETWORK_DEVICE',
    'APPLICATION',
    'DATABASE',
    'CLOUD_SERVICE',
    'MOBILE_DEVICE',
    'IOT_DEVICE',
    'OTHER'
);


ALTER TYPE public.assettype OWNER TO aegis_user;

--
-- Name: controlimplementationstatus; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.controlimplementationstatus AS ENUM (
    'IMPLEMENTED',
    'NOT_IMPLEMENTED',
    'PARTIALLY_IMPLEMENTED',
    'NOT_APPLICABLE',
    'PLANNED'
);


ALTER TYPE public.controlimplementationstatus OWNER TO aegis_user;

--
-- Name: evidencestatus; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.evidencestatus AS ENUM (
    'DRAFT',
    'UNDER_REVIEW',
    'APPROVED',
    'REJECTED',
    'EXPIRED',
    'ARCHIVED'
);


ALTER TYPE public.evidencestatus OWNER TO aegis_user;

--
-- Name: evidencetype; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.evidencetype AS ENUM (
    'DOCUMENT',
    'SCREENSHOT',
    'LOG_FILE',
    'CONFIGURATION',
    'POLICY',
    'PROCEDURE',
    'CERTIFICATE',
    'SCAN_RESULT',
    'REPORT',
    'OTHER'
);


ALTER TYPE public.evidencetype OWNER TO aegis_user;

--
-- Name: generationstatus; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.generationstatus AS ENUM (
    'STARTED',
    'COMPLETED',
    'FAILED'
);


ALTER TYPE public.generationstatus OWNER TO aegis_user;

--
-- Name: reportformat; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.reportformat AS ENUM (
    'PDF',
    'EXCEL',
    'CSV',
    'HTML',
    'JSON'
);


ALTER TYPE public.reportformat OWNER TO aegis_user;

--
-- Name: reportstatus; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.reportstatus AS ENUM (
    'DRAFT',
    'GENERATING',
    'COMPLETED',
    'FAILED',
    'SCHEDULED'
);


ALTER TYPE public.reportstatus OWNER TO aegis_user;

--
-- Name: reporttype; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.reporttype AS ENUM (
    'RISK_REGISTER',
    'ASSESSMENT_SUMMARY',
    'COMPLIANCE_STATUS',
    'EXECUTIVE_SUMMARY',
    'VULNERABILITY_REPORT',
    'TASK_STATUS',
    'CUSTOM'
);


ALTER TYPE public.reporttype OWNER TO aegis_user;

--
-- Name: riskcategory; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.riskcategory AS ENUM (
    'OPERATIONAL',
    'TECHNICAL',
    'STRATEGIC',
    'COMPLIANCE',
    'FINANCIAL',
    'REPUTATIONAL'
);


ALTER TYPE public.riskcategory OWNER TO aegis_user;

--
-- Name: riskstatus; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.riskstatus AS ENUM (
    'IDENTIFIED',
    'ASSESSED',
    'MITIGATING',
    'MONITORING',
    'ACCEPTED',
    'CLOSED'
);


ALTER TYPE public.riskstatus OWNER TO aegis_user;

--
-- Name: taskpriority; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.taskpriority AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);


ALTER TYPE public.taskpriority OWNER TO aegis_user;

--
-- Name: taskstatus; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.taskstatus AS ENUM (
    'OPEN',
    'IN_PROGRESS',
    'AWAITING_REVIEW',
    'COMPLETED',
    'CANCELLED',
    'ON_HOLD'
);


ALTER TYPE public.taskstatus OWNER TO aegis_user;

--
-- Name: tasktype; Type: TYPE; Schema: public; Owner: aegis_user
--

CREATE TYPE public.tasktype AS ENUM (
    'REMEDIATION',
    'MITIGATION',
    'ASSESSMENT',
    'DOCUMENTATION',
    'REVIEW',
    'COMPLIANCE',
    'OTHER'
);


ALTER TYPE public.tasktype OWNER TO aegis_user;

--
-- Name: audit_trigger_function(); Type: FUNCTION; Schema: public; Owner: aegis_user
--

CREATE FUNCTION public.audit_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = NOW();
        NEW.updated_at = NOW();
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_trigger_function() OWNER TO aegis_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assessment_controls; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.assessment_controls (
    id integer NOT NULL,
    assessment_id integer NOT NULL,
    control_id integer NOT NULL,
    implementation_status public.controlimplementationstatus NOT NULL,
    implementation_score integer,
    effectiveness_rating character varying(20),
    control_narrative text,
    testing_procedures text,
    evidence_summary text,
    ai_generated_narrative text,
    ai_confidence_score integer,
    ai_last_updated timestamp with time zone,
    assessor_notes text,
    testing_date timestamp with time zone,
    next_testing_date timestamp with time zone,
    review_status character varying(50),
    reviewed_by_id integer,
    reviewed_at timestamp with time zone,
    review_comments text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.assessment_controls OWNER TO aegis_user;

--
-- Name: assessment_controls_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.assessment_controls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.assessment_controls_id_seq OWNER TO aegis_user;

--
-- Name: assessment_controls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.assessment_controls_id_seq OWNED BY public.assessment_controls.id;


--
-- Name: assessments; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.assessments (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    framework_id integer NOT NULL,
    asset_id integer,
    scope_description text,
    assessment_type character varying(50),
    methodology character varying(100),
    status public.assessmentstatus,
    start_date timestamp with time zone,
    target_completion_date timestamp with time zone,
    actual_completion_date timestamp with time zone,
    created_by_id integer NOT NULL,
    lead_assessor_id integer,
    overall_score integer,
    maturity_level character varying(20),
    completion_percentage double precision,
    total_controls integer,
    assessed_controls integer,
    gap_analysis_data text,
    risk_generation_status character varying(50),
    tags text,
    custom_fields text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.assessments OWNER TO aegis_user;

--
-- Name: assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.assessments_id_seq OWNER TO aegis_user;

--
-- Name: assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.assessments_id_seq OWNED BY public.assessments.id;


--
-- Name: asset_categories; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.asset_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(7),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.asset_categories OWNER TO aegis_user;

--
-- Name: asset_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.asset_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.asset_categories_id_seq OWNER TO aegis_user;

--
-- Name: asset_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.asset_categories_id_seq OWNED BY public.asset_categories.id;


--
-- Name: assets; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.assets (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    asset_type public.assettype NOT NULL,
    criticality public.assetcriticality,
    category_id integer,
    owner_id integer,
    ip_address character varying(45),
    hostname character varying(255),
    operating_system character varying(100),
    version character varying(50),
    location character varying(255),
    environment character varying(50),
    business_unit character varying(100),
    cost_center character varying(50),
    compliance_scope text,
    status character varying(50),
    purchase_date timestamp with time zone,
    warranty_expiry timestamp with time zone,
    last_scan_date timestamp with time zone,
    tags text,
    custom_fields text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    created_by integer
);


ALTER TABLE public.assets OWNER TO aegis_user;

--
-- Name: assets_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.assets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.assets_id_seq OWNER TO aegis_user;

--
-- Name: assets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.assets_id_seq OWNED BY public.assets.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    event_type character varying(100) NOT NULL,
    entity_type character varying(100),
    entity_id integer,
    user_id integer,
    session_id character varying(255),
    ip_address character varying(45),
    user_agent character varying(1000),
    action character varying(255) NOT NULL,
    description text,
    old_values json,
    new_values json,
    source character varying(100),
    correlation_id character varying(255),
    risk_level character varying(20),
    compliance_relevant boolean,
    additional_data json,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO aegis_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_logs_id_seq OWNER TO aegis_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: control_mappings; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.control_mappings (
    id integer NOT NULL,
    control_id integer NOT NULL,
    mapped_framework character varying(100),
    mapped_control_id character varying(50),
    mapping_type character varying(50),
    confidence_level character varying(20),
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.control_mappings OWNER TO aegis_user;

--
-- Name: control_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.control_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.control_mappings_id_seq OWNER TO aegis_user;

--
-- Name: control_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.control_mappings_id_seq OWNED BY public.control_mappings.id;


--
-- Name: controls; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.controls (
    id integer NOT NULL,
    framework_id integer NOT NULL,
    control_id character varying(50) NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    guidance text,
    parent_id integer,
    level integer,
    sort_order double precision,
    control_type character varying(50),
    implementation_status character varying(50),
    testing_frequency character varying(50),
    risk_level character varying(20),
    compliance_references text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.controls OWNER TO aegis_user;

--
-- Name: controls_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.controls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.controls_id_seq OWNER TO aegis_user;

--
-- Name: controls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.controls_id_seq OWNED BY public.controls.id;


--
-- Name: custom_integrations; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.custom_integrations (
    id integer NOT NULL,
    integration_id integer NOT NULL,
    template_id integer NOT NULL,
    configuration_values json,
    field_mappings json,
    data_transformations json,
    is_active boolean,
    last_validation timestamp with time zone,
    validation_errors json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.custom_integrations OWNER TO aegis_user;

--
-- Name: custom_integrations_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.custom_integrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.custom_integrations_id_seq OWNER TO aegis_user;

--
-- Name: custom_integrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.custom_integrations_id_seq OWNED BY public.custom_integrations.id;


--
-- Name: evidence; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.evidence (
    id integer NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    file_name character varying(255),
    file_path character varying(1000),
    file_size integer,
    file_type character varying(100),
    file_hash character varying(64),
    evidence_type public.evidencetype NOT NULL,
    category character varying(100),
    subcategory character varying(100),
    content_summary text,
    extracted_text text,
    ai_analysis text,
    ai_confidence_score integer,
    ai_last_analyzed timestamp with time zone,
    version character varying(20),
    previous_version_id integer,
    is_current_version boolean,
    status public.evidencestatus,
    uploaded_by_id integer NOT NULL,
    owner_id integer,
    access_level character varying(50),
    effective_date timestamp with time zone,
    expiry_date timestamp with time zone,
    review_date timestamp with time zone,
    compliance_scope text,
    reviewed_by_id integer,
    reviewed_at timestamp with time zone,
    review_comments text,
    tags text,
    custom_fields text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.evidence OWNER TO aegis_user;

--
-- Name: evidence_controls; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.evidence_controls (
    id integer NOT NULL,
    evidence_id integer NOT NULL,
    control_id integer NOT NULL,
    relationship_type character varying(50),
    relevance_score integer,
    description text,
    ai_relevance_analysis text,
    ai_confidence_score integer,
    ai_last_analyzed timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    created_by integer
);


ALTER TABLE public.evidence_controls OWNER TO aegis_user;

--
-- Name: evidence_controls_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.evidence_controls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.evidence_controls_id_seq OWNER TO aegis_user;

--
-- Name: evidence_controls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.evidence_controls_id_seq OWNED BY public.evidence_controls.id;


--
-- Name: evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.evidence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.evidence_id_seq OWNER TO aegis_user;

--
-- Name: evidence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.evidence_id_seq OWNED BY public.evidence.id;


--
-- Name: frameworks; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.frameworks (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    version character varying(50),
    description text,
    source_url character varying(500),
    is_active boolean,
    is_default boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.frameworks OWNER TO aegis_user;

--
-- Name: frameworks_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.frameworks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.frameworks_id_seq OWNER TO aegis_user;

--
-- Name: frameworks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.frameworks_id_seq OWNED BY public.frameworks.id;


--
-- Name: integration_logs; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.integration_logs (
    id integer NOT NULL,
    integration_id integer NOT NULL,
    event_type character varying(50) NOT NULL,
    event_status character varying(20) NOT NULL,
    message text,
    details json,
    duration_ms integer,
    records_processed integer,
    records_imported integer,
    records_failed integer,
    error_code character varying(50),
    error_message text,
    stack_trace text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.integration_logs OWNER TO aegis_user;

--
-- Name: integration_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.integration_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.integration_logs_id_seq OWNER TO aegis_user;

--
-- Name: integration_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.integration_logs_id_seq OWNED BY public.integration_logs.id;


--
-- Name: integration_schedules; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.integration_schedules (
    id integer NOT NULL,
    integration_id integer NOT NULL,
    is_enabled boolean,
    schedule_type character varying(20),
    interval_minutes integer,
    cron_expression character varying(100),
    last_run timestamp with time zone,
    next_run timestamp with time zone,
    run_count integer,
    failure_count integer,
    max_retries integer,
    retry_delay_minutes integer,
    timeout_minutes integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.integration_schedules OWNER TO aegis_user;

--
-- Name: integration_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.integration_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.integration_schedules_id_seq OWNER TO aegis_user;

--
-- Name: integration_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.integration_schedules_id_seq OWNED BY public.integration_schedules.id;


--
-- Name: integration_templates; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.integration_templates (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    category character varying(50) NOT NULL,
    version character varying(20),
    author character varying(100),
    configuration_schema json,
    connection_test_config json,
    sync_config json,
    capabilities json,
    supported_data_formats json,
    is_active boolean,
    is_public boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    created_by integer
);


ALTER TABLE public.integration_templates OWNER TO aegis_user;

--
-- Name: integration_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.integration_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.integration_templates_id_seq OWNER TO aegis_user;

--
-- Name: integration_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.integration_templates_id_seq OWNED BY public.integration_templates.id;


--
-- Name: integrations; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.integrations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    integration_type character varying(50) NOT NULL,
    endpoint_url character varying(500),
    api_key character varying(500),
    username character varying(255),
    password character varying(500),
    configuration json,
    is_active boolean,
    is_connected boolean,
    last_connection_test timestamp with time zone,
    last_sync timestamp with time zone,
    connection_error text,
    retry_count integer,
    description text,
    tags json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    created_by integer
);


ALTER TABLE public.integrations OWNER TO aegis_user;

--
-- Name: integrations_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.integrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.integrations_id_seq OWNER TO aegis_user;

--
-- Name: integrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.integrations_id_seq OWNED BY public.integrations.id;


--
-- Name: report_generation_history; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.report_generation_history (
    id integer NOT NULL,
    report_id integer,
    scheduled_report_id integer,
    template_id integer NOT NULL,
    status public.generationstatus NOT NULL,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    duration_seconds integer,
    file_size_bytes integer,
    record_count integer,
    error_message text,
    parameters_used json,
    filters_used json,
    triggered_by character varying(50),
    user_id integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.report_generation_history OWNER TO aegis_user;

--
-- Name: report_generation_history_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.report_generation_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.report_generation_history_id_seq OWNER TO aegis_user;

--
-- Name: report_generation_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.report_generation_history_id_seq OWNED BY public.report_generation_history.id;


--
-- Name: report_templates; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.report_templates (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    report_type public.reporttype NOT NULL,
    template_data json,
    layout_config json,
    style_config json,
    default_filters json,
    parameter_schema json,
    is_public boolean,
    is_system_template boolean,
    usage_count integer,
    created_by integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.report_templates OWNER TO aegis_user;

--
-- Name: report_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.report_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.report_templates_id_seq OWNER TO aegis_user;

--
-- Name: report_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.report_templates_id_seq OWNED BY public.report_templates.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.reports (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    report_type public.reporttype NOT NULL,
    template_id integer,
    status public.reportstatus,
    format public.reportformat,
    parameters json,
    filters json,
    file_name character varying(255),
    file_path character varying(1000),
    file_size integer,
    ai_summary text,
    ai_insights json,
    ai_confidence_score integer,
    is_scheduled boolean,
    schedule_config json,
    next_generation timestamp with time zone,
    recipients json,
    distribution_list character varying(500),
    generation_started timestamp with time zone,
    generation_completed timestamp with time zone,
    generation_duration integer,
    error_message text,
    download_count integer,
    last_downloaded timestamp with time zone,
    tags json,
    custom_fields json,
    created_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.reports OWNER TO aegis_user;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reports_id_seq OWNER TO aegis_user;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: risk_matrices; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.risk_matrices (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    likelihood_levels text,
    impact_levels text,
    risk_scores text,
    risk_levels text,
    is_default boolean,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.risk_matrices OWNER TO aegis_user;

--
-- Name: risk_matrices_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.risk_matrices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.risk_matrices_id_seq OWNER TO aegis_user;

--
-- Name: risk_matrices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.risk_matrices_id_seq OWNED BY public.risk_matrices.id;


--
-- Name: risk_scores; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.risk_scores (
    id integer NOT NULL,
    risk_id integer NOT NULL,
    likelihood_score integer,
    impact_score integer,
    total_score double precision,
    risk_level character varying(20),
    score_type character varying(20),
    likelihood_rationale text,
    impact_rationale text,
    scoring_methodology character varying(100),
    scored_by integer,
    scored_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.risk_scores OWNER TO aegis_user;

--
-- Name: risk_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.risk_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.risk_scores_id_seq OWNER TO aegis_user;

--
-- Name: risk_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.risk_scores_id_seq OWNED BY public.risk_scores.id;


--
-- Name: risks; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.risks (
    id integer NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    category public.riskcategory NOT NULL,
    subcategory character varying(100),
    risk_type character varying(100),
    source character varying(100),
    source_reference character varying(255),
    asset_id integer,
    affected_systems text,
    business_process character varying(255),
    risk_matrix_id integer,
    inherent_likelihood integer,
    inherent_impact integer,
    inherent_risk_score double precision,
    residual_likelihood integer,
    residual_impact integer,
    residual_risk_score double precision,
    risk_level character varying(20),
    threat_source character varying(255),
    vulnerability text,
    existing_controls text,
    control_effectiveness character varying(50),
    ai_generated_statement text,
    ai_risk_assessment text,
    ai_confidence_score integer,
    ai_last_updated timestamp with time zone,
    treatment_strategy character varying(50),
    treatment_rationale text,
    status public.riskstatus,
    owner_id integer,
    identified_date timestamp with time zone DEFAULT now(),
    target_resolution_date timestamp with time zone,
    actual_resolution_date timestamp with time zone,
    last_review_date timestamp with time zone,
    next_review_date timestamp with time zone,
    tags text,
    custom_fields text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    created_by integer
);


ALTER TABLE public.risks OWNER TO aegis_user;

--
-- Name: risks_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.risks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.risks_id_seq OWNER TO aegis_user;

--
-- Name: risks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.risks_id_seq OWNED BY public.risks.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    permissions text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.roles OWNER TO aegis_user;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO aegis_user;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: scheduled_reports; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.scheduled_reports (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    template_id integer NOT NULL,
    schedule_expression character varying(100) NOT NULL,
    parameters json,
    filters json,
    format public.reportformat NOT NULL,
    recipients json NOT NULL,
    is_active boolean,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    run_count integer,
    failure_count integer,
    last_error text,
    created_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.scheduled_reports OWNER TO aegis_user;

--
-- Name: scheduled_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.scheduled_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scheduled_reports_id_seq OWNER TO aegis_user;

--
-- Name: scheduled_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.scheduled_reports_id_seq OWNED BY public.scheduled_reports.id;


--
-- Name: settings; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.settings (
    id integer NOT NULL,
    category character varying(100) NOT NULL,
    key character varying(200) NOT NULL,
    value text,
    data_type character varying(50),
    is_encrypted boolean,
    description text,
    is_system boolean,
    validation_rules text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.settings OWNER TO aegis_user;

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.settings_id_seq OWNER TO aegis_user;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.settings_id_seq OWNED BY public.settings.id;


--
-- Name: task_comments; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.task_comments (
    id integer NOT NULL,
    task_id integer NOT NULL,
    user_id integer NOT NULL,
    comment text NOT NULL,
    comment_type character varying(50),
    is_internal boolean,
    is_system_generated boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.task_comments OWNER TO aegis_user;

--
-- Name: task_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.task_comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_comments_id_seq OWNER TO aegis_user;

--
-- Name: task_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.task_comments_id_seq OWNED BY public.task_comments.id;


--
-- Name: task_evidence; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.task_evidence (
    id integer NOT NULL,
    task_id integer NOT NULL,
    evidence_id integer NOT NULL,
    relationship_type character varying(50),
    description text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.task_evidence OWNER TO aegis_user;

--
-- Name: task_evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.task_evidence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_evidence_id_seq OWNER TO aegis_user;

--
-- Name: task_evidence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.task_evidence_id_seq OWNED BY public.task_evidence.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    task_type public.tasktype,
    category character varying(100),
    subcategory character varying(100),
    priority public.taskpriority,
    status public.taskstatus,
    risk_id integer,
    asset_id integer,
    assigned_to_id integer,
    created_by_id integer NOT NULL,
    start_date timestamp with time zone,
    due_date timestamp with time zone,
    completed_date timestamp with time zone,
    estimated_hours integer,
    actual_hours integer,
    progress_percentage integer,
    milestone_description text,
    ai_generated_plan text,
    ai_suggested_actions text,
    ai_confidence_score integer,
    ai_last_updated timestamp with time zone,
    requires_approval boolean,
    approval_status character varying(50),
    approved_by_id integer,
    approved_at timestamp with time zone,
    approval_comments text,
    estimated_cost character varying(50),
    actual_cost character varying(50),
    cost_center character varying(50),
    depends_on_tasks json,
    blocks_tasks json,
    dependency_validation_status character varying(50),
    status_history json,
    allowed_transitions json,
    workflow_stage character varying(100),
    workflow_rules json,
    milestones json,
    completion_criteria json,
    progress_notes text,
    progress_last_updated timestamp with time zone,
    progress_updated_by_id integer,
    auto_transition_rules json,
    notification_rules json,
    escalation_rules json,
    cycle_time_hours double precision,
    lead_time_hours double precision,
    blocked_time_hours double precision,
    rework_count integer,
    tags json,
    custom_fields json,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.tasks OWNER TO aegis_user;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO aegis_user;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: threat_intel_data; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.threat_intel_data (
    id integer NOT NULL,
    integration_id integer NOT NULL,
    intel_type character varying(50),
    indicator_type character varying(50),
    indicator_value character varying(1000),
    threat_name character varying(255),
    description text,
    threat_actor character varying(255),
    campaign character varying(255),
    malware_family character varying(255),
    confidence_level character varying(20),
    severity character varying(20),
    first_seen timestamp with time zone,
    last_seen timestamp with time zone,
    tags json,
    tlp character varying(20),
    raw_data json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.threat_intel_data OWNER TO aegis_user;

--
-- Name: threat_intel_data_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.threat_intel_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.threat_intel_data_id_seq OWNER TO aegis_user;

--
-- Name: threat_intel_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.threat_intel_data_id_seq OWNED BY public.threat_intel_data.id;


--
-- Name: user_activities; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.user_activities (
    id integer NOT NULL,
    user_id integer NOT NULL,
    activity_type character varying(100) NOT NULL,
    activity_description text,
    ip_address character varying(45),
    user_agent text,
    session_id character varying(255),
    resource_type character varying(100),
    resource_id integer,
    activity_metadata json,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.user_activities OWNER TO aegis_user;

--
-- Name: user_activities_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.user_activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_activities_id_seq OWNER TO aegis_user;

--
-- Name: user_activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.user_activities_id_seq OWNED BY public.user_activities.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_at timestamp with time zone DEFAULT now(),
    assigned_by integer
);


ALTER TABLE public.user_roles OWNER TO aegis_user;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_roles_id_seq OWNER TO aegis_user;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    full_name character varying(255),
    hashed_password character varying(255),
    is_active boolean,
    is_verified boolean,
    last_login timestamp with time zone,
    last_activity timestamp with time zone,
    failed_login_attempts integer,
    locked_until timestamp with time zone,
    password_changed_at timestamp with time zone,
    login_count integer,
    profile_picture character varying(500),
    department character varying(100),
    job_title character varying(100),
    phone character varying(20),
    azure_ad_id character varying(255),
    preferences text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO aegis_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO aegis_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vulnerability_data; Type: TABLE; Schema: public; Owner: aegis_user
--

CREATE TABLE public.vulnerability_data (
    id integer NOT NULL,
    integration_id integer NOT NULL,
    asset_id integer,
    vulnerability_id character varying(100),
    title character varying(500) NOT NULL,
    description text,
    severity character varying(20),
    cvss_score double precision,
    cvss_vector character varying(200),
    port character varying(20),
    protocol character varying(20),
    service character varying(100),
    scan_id character varying(100),
    scan_date timestamp with time zone,
    scanner_name character varying(100),
    status character varying(50),
    first_detected timestamp with time zone,
    last_detected timestamp with time zone,
    solution text,
    workaround text,
    risk_score double precision,
    business_impact text,
    raw_data json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.vulnerability_data OWNER TO aegis_user;

--
-- Name: vulnerability_data_id_seq; Type: SEQUENCE; Schema: public; Owner: aegis_user
--

CREATE SEQUENCE public.vulnerability_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vulnerability_data_id_seq OWNER TO aegis_user;

--
-- Name: vulnerability_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aegis_user
--

ALTER SEQUENCE public.vulnerability_data_id_seq OWNED BY public.vulnerability_data.id;


--
-- Name: assessment_controls id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessment_controls ALTER COLUMN id SET DEFAULT nextval('public.assessment_controls_id_seq'::regclass);


--
-- Name: assessments id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessments ALTER COLUMN id SET DEFAULT nextval('public.assessments_id_seq'::regclass);


--
-- Name: asset_categories id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.asset_categories ALTER COLUMN id SET DEFAULT nextval('public.asset_categories_id_seq'::regclass);


--
-- Name: assets id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assets ALTER COLUMN id SET DEFAULT nextval('public.assets_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: control_mappings id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.control_mappings ALTER COLUMN id SET DEFAULT nextval('public.control_mappings_id_seq'::regclass);


--
-- Name: controls id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.controls ALTER COLUMN id SET DEFAULT nextval('public.controls_id_seq'::regclass);


--
-- Name: custom_integrations id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.custom_integrations ALTER COLUMN id SET DEFAULT nextval('public.custom_integrations_id_seq'::regclass);


--
-- Name: evidence id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence ALTER COLUMN id SET DEFAULT nextval('public.evidence_id_seq'::regclass);


--
-- Name: evidence_controls id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence_controls ALTER COLUMN id SET DEFAULT nextval('public.evidence_controls_id_seq'::regclass);


--
-- Name: frameworks id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.frameworks ALTER COLUMN id SET DEFAULT nextval('public.frameworks_id_seq'::regclass);


--
-- Name: integration_logs id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_logs ALTER COLUMN id SET DEFAULT nextval('public.integration_logs_id_seq'::regclass);


--
-- Name: integration_schedules id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_schedules ALTER COLUMN id SET DEFAULT nextval('public.integration_schedules_id_seq'::regclass);


--
-- Name: integration_templates id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_templates ALTER COLUMN id SET DEFAULT nextval('public.integration_templates_id_seq'::regclass);


--
-- Name: integrations id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integrations ALTER COLUMN id SET DEFAULT nextval('public.integrations_id_seq'::regclass);


--
-- Name: report_generation_history id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_generation_history ALTER COLUMN id SET DEFAULT nextval('public.report_generation_history_id_seq'::regclass);


--
-- Name: report_templates id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_templates ALTER COLUMN id SET DEFAULT nextval('public.report_templates_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: risk_matrices id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risk_matrices ALTER COLUMN id SET DEFAULT nextval('public.risk_matrices_id_seq'::regclass);


--
-- Name: risk_scores id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risk_scores ALTER COLUMN id SET DEFAULT nextval('public.risk_scores_id_seq'::regclass);


--
-- Name: risks id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risks ALTER COLUMN id SET DEFAULT nextval('public.risks_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: scheduled_reports id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.scheduled_reports ALTER COLUMN id SET DEFAULT nextval('public.scheduled_reports_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.settings ALTER COLUMN id SET DEFAULT nextval('public.settings_id_seq'::regclass);


--
-- Name: task_comments id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_comments ALTER COLUMN id SET DEFAULT nextval('public.task_comments_id_seq'::regclass);


--
-- Name: task_evidence id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_evidence ALTER COLUMN id SET DEFAULT nextval('public.task_evidence_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: threat_intel_data id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.threat_intel_data ALTER COLUMN id SET DEFAULT nextval('public.threat_intel_data_id_seq'::regclass);


--
-- Name: user_activities id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_activities ALTER COLUMN id SET DEFAULT nextval('public.user_activities_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vulnerability_data id; Type: DEFAULT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.vulnerability_data ALTER COLUMN id SET DEFAULT nextval('public.vulnerability_data_id_seq'::regclass);


--
-- Data for Name: assessment_controls; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.assessment_controls (id, assessment_id, control_id, implementation_status, implementation_score, effectiveness_rating, control_narrative, testing_procedures, evidence_summary, ai_generated_narrative, ai_confidence_score, ai_last_updated, assessor_notes, testing_date, next_testing_date, review_status, reviewed_by_id, reviewed_at, review_comments, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.assessments (id, name, description, framework_id, asset_id, scope_description, assessment_type, methodology, status, start_date, target_completion_date, actual_completion_date, created_by_id, lead_assessor_id, overall_score, maturity_level, completion_percentage, total_controls, assessed_controls, gap_analysis_data, risk_generation_status, tags, custom_fields, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: asset_categories; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.asset_categories (id, name, description, color, is_active, created_at, updated_at) FROM stdin;
1	Servers	Physical and virtual servers	\N	t	2025-07-24 16:41:26.714423+00	\N
2	Workstations	Employee workstations and laptops	\N	t	2025-07-24 16:41:26.714423+00	\N
3	Network Equipment	Routers, switches, firewalls	\N	t	2025-07-24 16:41:26.714423+00	\N
4	Databases	Database systems and repositories	\N	t	2025-07-24 16:41:26.714423+00	\N
5	Applications	Software applications and systems	\N	t	2025-07-24 16:41:26.714423+00	\N
6	Cloud Services	Cloud-based services and platforms	\N	t	2025-07-24 16:41:26.714423+00	\N
7	Mobile Devices	Smartphones, tablets, and mobile devices	\N	t	2025-07-24 16:41:26.714423+00	\N
8	IoT Devices	Internet of Things devices	\N	t	2025-07-24 16:41:26.714423+00	\N
9	Storage Systems	Data storage systems and devices	\N	t	2025-07-24 16:41:26.714423+00	\N
10	Network	Network infrastructure	#10B981	t	2025-07-25 03:32:56.709824+00	\N
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.assets (id, name, description, asset_type, criticality, category_id, owner_id, ip_address, hostname, operating_system, version, location, environment, business_unit, cost_center, compliance_scope, status, purchase_date, warranty_expiry, last_scan_date, tags, custom_fields, is_active, created_at, updated_at, created_by) FROM stdin;
1	Web Server 01	Primary web server hosting customer portal	SERVER	CRITICAL	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	active	\N	\N	\N	\N	\N	t	2025-07-25 03:32:56.718557+00	\N	\N
2	Database Server	Main customer database server	DATABASE	CRITICAL	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	active	\N	\N	\N	\N	\N	t	2025-07-25 03:32:56.718557+00	\N	\N
3	Firewall	Perimeter firewall	NETWORK_DEVICE	HIGH	10	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	active	\N	\N	\N	\N	\N	t	2025-07-25 03:32:56.718557+00	\N	\N
4	Employee Workstation	Standard employee workstation	WORKSTATION	MEDIUM	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	active	\N	\N	\N	\N	\N	t	2025-07-25 03:32:56.718557+00	\N	\N
5	CRM Application	Customer relationship management system	APPLICATION	HIGH	5	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	active	\N	\N	\N	\N	\N	t	2025-07-25 03:32:56.718557+00	\N	\N
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.audit_logs (id, event_type, entity_type, entity_id, user_id, session_id, ip_address, user_agent, action, description, old_values, new_values, source, correlation_id, risk_level, compliance_relevant, additional_data, "timestamp") FROM stdin;
1	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 16:41:32.03259+00
2	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 16:42:23.3199+00
3	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin@uat.aegis.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 16:43:24.420621+00
4	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 16:43:24.525579+00
5	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 17:09:51.5049+00
6	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin@uat.aegis.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 17:10:19.529323+00
7	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 17:10:19.647783+00
8	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin@uat-test.aegis.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 17:28:22.792787+00
9	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 17:29:58.998828+00
10	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 17:36:43.121248+00
11	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 17:50:15.179259+00
12	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:11:41.212476+00
13	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:16:43.112084+00
14	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:33:30.096044+00
15	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:37:17.817744+00
16	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:39:17.524447+00
17	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:40:17.149073+00
18	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:47:27.279195+00
19	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:49:22.804009+00
20	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 18:51:42.961688+00
21	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:00:04.208491+00
22	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:01:15.478264+00
23	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:01:30.036792+00
24	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:02:02.322903+00
25	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:03:40.96042+00
26	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:03:46.245813+00
27	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin@aegis-platform.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 19:04:42.070309+00
28	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin@aegis-platform.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 19:04:51.981183+00
29	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin@aegis-platform.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 19:05:18.845743+00
30	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: admin@aegis-platform.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 19:13:16.745764+00
31	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:17:10.472716+00
32	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:20:05.810334+00
33	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:20:47.590864+00
34	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:22:16.987858+00
35	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:22:50.67572+00
36	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:26:24.032215+00
37	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:26:58.663284+00
38	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:27:30.01459+00
39	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:33:12.249729+00
40	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:34:29.51119+00
41	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:35:56.938535+00
42	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:36:20.652816+00
43	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:45:49.00139+00
44	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:46:14.59149+00
45	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:46:35.579474+00
46	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 19:47:28.963487+00
47	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:06:23.040816+00
48	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:06:41.785483+00
49	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:06:55.66591+00
50	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:08:02.84137+00
51	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:09:38.208489+00
52	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:10:15.389445+00
53	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:10:37.832985+00
54	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:12:18.458518+00
55	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:17:15.905431+00
56	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:17:40.56934+00
57	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:17:52.556523+00
58	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:18:59.161181+00
59	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:19:23.512424+00
60	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:19:48.792161+00
61	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@aegis.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-24 20:24:15.550025+00
62	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-24 20:24:31.831054+00
63	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 01:51:07.124394+00
64	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 02:02:23.74119+00
65	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 02:19:07.799016+00
66	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 02:35:56.63188+00
67	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 02:36:51.666316+00
68	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 02:44:38.632372+00
69	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 02:49:30.320403+00
70	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:02:39.144036+00
71	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:06:18.785527+00
72	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:13:13.060426+00
73	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:17:27.844773+00
74	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:40:45.114867+00
75	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:53:31.558363+00
76	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:53:44.851845+00
77	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 03:54:36.517288+00
78	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:54.423903+00
79	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:54.812421+00
80	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:55.951463+00
81	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:56.313649+00
82	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:56.752535+00
83	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:57.131528+00
84	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:57.552028+00
85	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:57.953948+00
86	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:58.991017+00
87	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:59.362957+00
88	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:57:59.818427+00
89	login_failed	user	\N	\N	\N	\N	\N	Failed login attempt	Failed login attempt for: test@example.com	\N	\N	web_ui	\N	medium	f	\N	2025-07-25 03:58:00.199098+00
90	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 04:05:01.05011+00
91	login	user	1	1	\N	\N	\N	User login	User logged in: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 04:14:55.43008+00
92	logout	user	1	1	\N	\N	\N	User logout	User logged out: admin@aegis-platform.com	\N	\N	web_ui	\N	low	f	\N	2025-07-25 04:26:27.743042+00
\.


--
-- Data for Name: control_mappings; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.control_mappings (id, control_id, mapped_framework, mapped_control_id, mapping_type, confidence_level, notes, created_at) FROM stdin;
\.


--
-- Data for Name: controls; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.controls (id, framework_id, control_id, title, description, guidance, parent_id, level, sort_order, control_type, implementation_status, testing_frequency, risk_level, compliance_references, is_active, created_at, updated_at) FROM stdin;
1	1	ID.AM-1	Physical devices and systems are inventoried	Physical devices and systems within the organization are inventoried	Category: Asset Management, Function: Identify	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
2	1	ID.AM-2	Software platforms and applications are inventoried	Software platforms and applications within the organization are inventoried	Category: Asset Management, Function: Identify	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
3	1	ID.GV-1	Organizational cybersecurity policy is established	Organizational cybersecurity policy is established and communicated	Category: Governance, Function: Identify	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
4	1	PR.AC-1	Identities and credentials are issued and managed	Identities and credentials are issued, managed, verified, revoked, and audited	Category: Identity Management, Function: Protect	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
5	1	PR.AC-3	Remote access is managed	Remote access is managed according to organizational policy	Category: Identity Management, Function: Protect	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
6	1	PR.DS-1	Data-at-rest is protected	Data-at-rest is protected with appropriate encryption and access controls	Category: Data Security, Function: Protect	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
7	1	DE.AE-1	A baseline of network operations is established	A baseline of network operations and expected data flows is established and managed	Category: Anomalies and Events, Function: Detect	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
8	1	DE.CM-1	Networks are monitored	The network is monitored to detect potential cybersecurity events	Category: Security Continuous Monitoring, Function: Detect	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
9	1	RS.RP-1	Response plan is executed	Response plan is executed during or after an incident	Category: Response Planning, Function: Respond	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
10	1	RS.CO-2	Incidents are reported	Incidents are reported consistent with established criteria	Category: Communications, Function: Respond	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
11	1	RC.RP-1	Recovery plan is executed	Recovery plan is executed during or after a cybersecurity incident	Category: Recovery Planning, Function: Recover	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
12	1	RC.IM-1	Recovery plans incorporate lessons learned	Recovery plans incorporate lessons learned from organizational experience	Category: Improvements, Function: Recover	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.709815+00	\N
13	2	CIS-1	Inventory and Control of Hardware Assets	Actively manage all hardware devices to ensure authorized devices are present	Category: Basic CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
14	2	CIS-2	Inventory and Control of Software Assets	Actively manage all software on the network to ensure authorized software is present	Category: Basic CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
15	2	CIS-3	Continuous Vulnerability Management	Continuously acquire, assess, and take action on new information	Category: Basic CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
16	2	CIS-4	Controlled Use of Administrative Privileges	Processes and tools used to track, control, prevent, and correct use of administrative privileges	Category: Basic CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
17	2	CIS-5	Secure Configuration for Hardware and Software	Establish, implement, and actively manage security configurations	Category: Basic CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
18	2	CIS-6	Maintenance, Monitoring, and Analysis of Audit Logs	Collect, manage, and analyze audit logs to detect anomalous activity	Category: Basic CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
19	2	CIS-7	Email and Web Browser Protections	Minimize the attack surface and opportunities for attackers	Category: Foundational CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
20	2	CIS-8	Malware Defenses	Control the installation, spread, and execution of malicious code	Category: Foundational CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
21	2	CIS-9	Limitation and Control of Network Ports	Manage network infrastructure to limit communications	Category: Foundational CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
22	2	CIS-10	Data Recovery Capabilities	Processes and tools used to properly back up critical information	Category: Foundational CIS Controls, Function: Foundational	\N	1	0	preventive	manual	\N	\N	\N	t	2025-07-24 16:41:26.712505+00	\N
\.


--
-- Data for Name: custom_integrations; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.custom_integrations (id, integration_id, template_id, configuration_values, field_mappings, data_transformations, is_active, last_validation, validation_errors, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: evidence; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.evidence (id, title, description, file_name, file_path, file_size, file_type, file_hash, evidence_type, category, subcategory, content_summary, extracted_text, ai_analysis, ai_confidence_score, ai_last_analyzed, version, previous_version_id, is_current_version, status, uploaded_by_id, owner_id, access_level, effective_date, expiry_date, review_date, compliance_scope, reviewed_by_id, reviewed_at, review_comments, tags, custom_fields, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: evidence_controls; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.evidence_controls (id, evidence_id, control_id, relationship_type, relevance_score, description, ai_relevance_analysis, ai_confidence_score, ai_last_analyzed, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: frameworks; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.frameworks (id, name, version, description, source_url, is_active, is_default, created_at, updated_at) FROM stdin;
1	NIST Cybersecurity Framework	1.1	A framework to improve cybersecurity risk management	https://www.nist.gov/cyberframework	t	f	2025-07-24 16:41:26.708339+00	\N
2	CIS Controls	8.0	Critical Security Controls for Effective Cyber Defense	https://www.cisecurity.org/controls	t	f	2025-07-24 16:41:26.712128+00	\N
\.


--
-- Data for Name: integration_logs; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.integration_logs (id, integration_id, event_type, event_status, message, details, duration_ms, records_processed, records_imported, records_failed, error_code, error_message, stack_trace, created_at) FROM stdin;
\.


--
-- Data for Name: integration_schedules; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.integration_schedules (id, integration_id, is_enabled, schedule_type, interval_minutes, cron_expression, last_run, next_run, run_count, failure_count, max_retries, retry_delay_minutes, timeout_minutes, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: integration_templates; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.integration_templates (id, name, description, category, version, author, configuration_schema, connection_test_config, sync_config, capabilities, supported_data_formats, is_active, is_public, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: integrations; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.integrations (id, name, integration_type, endpoint_url, api_key, username, password, configuration, is_active, is_connected, last_connection_test, last_sync, connection_error, retry_count, description, tags, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: report_generation_history; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.report_generation_history (id, report_id, scheduled_report_id, template_id, status, started_at, completed_at, duration_seconds, file_size_bytes, record_count, error_message, parameters_used, filters_used, triggered_by, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: report_templates; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.report_templates (id, name, description, report_type, template_data, layout_config, style_config, default_filters, parameter_schema, is_public, is_system_template, usage_count, created_by, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.reports (id, name, description, report_type, template_id, status, format, parameters, filters, file_name, file_path, file_size, ai_summary, ai_insights, ai_confidence_score, is_scheduled, schedule_config, next_generation, recipients, distribution_list, generation_started, generation_completed, generation_duration, error_message, download_count, last_downloaded, tags, custom_fields, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: risk_matrices; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.risk_matrices (id, name, description, likelihood_levels, impact_levels, risk_scores, risk_levels, is_default, is_active, created_at, updated_at) FROM stdin;
1	Standard 5x5 Risk Matrix	Standard 5x5 qualitative risk assessment matrix	{"very_low": {"value": 1, "label": "Very Low", "description": "Rare occurrence"}, "low": {"value": 2, "label": "Low", "description": "Unlikely to occur"}, "medium": {"value": 3, "label": "Medium", "description": "Possible to occur"}, "high": {"value": 4, "label": "High", "description": "Likely to occur"}, "very_high": {"value": 5, "label": "Very High", "description": "Almost certain to occur"}}	{"very_low": {"value": 1, "label": "Very Low", "description": "Minimal impact"}, "low": {"value": 2, "label": "Low", "description": "Minor impact"}, "medium": {"value": 3, "label": "Medium", "description": "Moderate impact"}, "high": {"value": 4, "label": "High", "description": "Major impact"}, "very_high": {"value": 5, "label": "Very High", "description": "Severe impact"}}	\N	{"1-4": "low", "5-9": "medium", "10-14": "high", "15-25": "critical"}	t	t	2025-07-24 16:41:26.715476+00	\N
\.


--
-- Data for Name: risk_scores; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.risk_scores (id, risk_id, likelihood_score, impact_score, total_score, risk_level, score_type, likelihood_rationale, impact_rationale, scoring_methodology, scored_by, scored_at) FROM stdin;
\.


--
-- Data for Name: risks; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.risks (id, title, description, category, subcategory, risk_type, source, source_reference, asset_id, affected_systems, business_process, risk_matrix_id, inherent_likelihood, inherent_impact, inherent_risk_score, residual_likelihood, residual_impact, residual_risk_score, risk_level, threat_source, vulnerability, existing_controls, control_effectiveness, ai_generated_statement, ai_risk_assessment, ai_confidence_score, ai_last_updated, treatment_strategy, treatment_rationale, status, owner_id, identified_date, target_resolution_date, actual_resolution_date, last_review_date, next_review_date, tags, custom_fields, is_active, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.roles (id, name, description, permissions, is_active, created_at, updated_at) FROM stdin;
1	admin	System Administrator with full access	{"users": ["create", "read", "update", "delete"], "assets": ["create", "read", "update", "delete"], "risks": ["create", "read", "update", "delete"], "assessments": ["create", "read", "update", "delete"], "frameworks": ["create", "read", "update", "delete"], "tasks": ["create", "read", "update", "delete"], "evidence": ["create", "read", "update", "delete"], "reports": ["create", "read", "update", "delete"], "integrations": ["create", "read", "update", "delete"], "ai_services": ["create", "read", "update", "delete"]}	t	2025-07-24 16:41:26.504662+00	\N
2	analyst	Cybersecurity Analyst with assessment and analysis capabilities	{"assets": ["read", "update"], "risks": ["create", "read", "update"], "assessments": ["create", "read", "update"], "frameworks": ["read"], "tasks": ["create", "read", "update"], "evidence": ["create", "read", "update"], "reports": ["create", "read"], "integrations": ["read"], "ai_services": ["read"]}	t	2025-07-24 16:41:26.504662+00	\N
3	readonly	Read-only access to all modules	{"assets": ["read"], "risks": ["read"], "assessments": ["read"], "frameworks": ["read"], "tasks": ["read"], "evidence": ["read"], "reports": ["read"], "integrations": ["read"], "ai_services": ["read"]}	t	2025-07-24 16:41:26.504662+00	\N
\.


--
-- Data for Name: scheduled_reports; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.scheduled_reports (id, name, description, template_id, schedule_expression, parameters, filters, format, recipients, is_active, last_run_at, next_run_at, run_count, failure_count, last_error, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.settings (id, category, key, value, data_type, is_encrypted, description, is_system, validation_rules, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_comments; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.task_comments (id, task_id, user_id, comment, comment_type, is_internal, is_system_generated, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_evidence; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.task_evidence (id, task_id, evidence_id, relationship_type, description, created_at) FROM stdin;
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.tasks (id, title, description, task_type, category, subcategory, priority, status, risk_id, asset_id, assigned_to_id, created_by_id, start_date, due_date, completed_date, estimated_hours, actual_hours, progress_percentage, milestone_description, ai_generated_plan, ai_suggested_actions, ai_confidence_score, ai_last_updated, requires_approval, approval_status, approved_by_id, approved_at, approval_comments, estimated_cost, actual_cost, cost_center, depends_on_tasks, blocks_tasks, dependency_validation_status, status_history, allowed_transitions, workflow_stage, workflow_rules, milestones, completion_criteria, progress_notes, progress_last_updated, progress_updated_by_id, auto_transition_rules, notification_rules, escalation_rules, cycle_time_hours, lead_time_hours, blocked_time_hours, rework_count, tags, custom_fields, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: threat_intel_data; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.threat_intel_data (id, integration_id, intel_type, indicator_type, indicator_value, threat_name, description, threat_actor, campaign, malware_family, confidence_level, severity, first_seen, last_seen, tags, tlp, raw_data, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_activities; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.user_activities (id, user_id, activity_type, activity_description, ip_address, user_agent, session_id, resource_type, resource_id, activity_metadata, created_at) FROM stdin;
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.user_roles (id, user_id, role_id, assigned_at, assigned_by) FROM stdin;
1	1	1	2025-07-24 16:41:26.705883+00	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.users (id, email, username, full_name, hashed_password, is_active, is_verified, last_login, last_activity, failed_login_attempts, locked_until, password_changed_at, login_count, profile_picture, department, job_title, phone, azure_ad_id, preferences, created_at, updated_at) FROM stdin;
2	greattkiffy@gmail.com	greattkiffy	Great Iffy	$2b$12$5nwJJ9vriH/0SIypHNJqw.Xa8NlAVqiR3KQZBr5GYNVcSC1CEQnb2	t	t	\N	\N	0	\N	2025-07-25 02:03:57.412+00	0	\N				\N	\N	2025-07-25 02:03:57.20254+00	\N
1	admin@aegis-platform.com	admin	System Administrator	$2b$12$0zp0ymR6fCn4EeUjFeJai.8KvbDeD3HSzLYt39lIw5CF/wcHoHWue	t	t	2025-07-25 04:14:55.428757+00	\N	0	\N	\N	0	\N	\N	\N	\N	\N	\N	2025-07-24 16:41:26.50891+00	2025-07-25 04:14:55.12954+00
\.


--
-- Data for Name: vulnerability_data; Type: TABLE DATA; Schema: public; Owner: aegis_user
--

COPY public.vulnerability_data (id, integration_id, asset_id, vulnerability_id, title, description, severity, cvss_score, cvss_vector, port, protocol, service, scan_id, scan_date, scanner_name, status, first_detected, last_detected, solution, workaround, risk_score, business_impact, raw_data, created_at, updated_at) FROM stdin;
\.


--
-- Name: assessment_controls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.assessment_controls_id_seq', 1, false);


--
-- Name: assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.assessments_id_seq', 1, false);


--
-- Name: asset_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.asset_categories_id_seq', 10, true);


--
-- Name: assets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.assets_id_seq', 5, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 92, true);


--
-- Name: control_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.control_mappings_id_seq', 1, false);


--
-- Name: controls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.controls_id_seq', 22, true);


--
-- Name: custom_integrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.custom_integrations_id_seq', 1, false);


--
-- Name: evidence_controls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.evidence_controls_id_seq', 1, false);


--
-- Name: evidence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.evidence_id_seq', 1, false);


--
-- Name: frameworks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.frameworks_id_seq', 2, true);


--
-- Name: integration_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.integration_logs_id_seq', 1, false);


--
-- Name: integration_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.integration_schedules_id_seq', 1, false);


--
-- Name: integration_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.integration_templates_id_seq', 1, false);


--
-- Name: integrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.integrations_id_seq', 1, false);


--
-- Name: report_generation_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.report_generation_history_id_seq', 1, false);


--
-- Name: report_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.report_templates_id_seq', 1, false);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.reports_id_seq', 1, false);


--
-- Name: risk_matrices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.risk_matrices_id_seq', 1, true);


--
-- Name: risk_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.risk_scores_id_seq', 1, false);


--
-- Name: risks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.risks_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- Name: scheduled_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.scheduled_reports_id_seq', 1, false);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.settings_id_seq', 1, false);


--
-- Name: task_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.task_comments_id_seq', 1, false);


--
-- Name: task_evidence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.task_evidence_id_seq', 1, false);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, false);


--
-- Name: threat_intel_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.threat_intel_data_id_seq', 1, false);


--
-- Name: user_activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.user_activities_id_seq', 1, false);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: vulnerability_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: aegis_user
--

SELECT pg_catalog.setval('public.vulnerability_data_id_seq', 1, false);


--
-- Name: assessment_controls assessment_controls_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessment_controls
    ADD CONSTRAINT assessment_controls_pkey PRIMARY KEY (id);


--
-- Name: assessments assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_pkey PRIMARY KEY (id);


--
-- Name: asset_categories asset_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.asset_categories
    ADD CONSTRAINT asset_categories_pkey PRIMARY KEY (id);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: control_mappings control_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.control_mappings
    ADD CONSTRAINT control_mappings_pkey PRIMARY KEY (id);


--
-- Name: controls controls_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.controls
    ADD CONSTRAINT controls_pkey PRIMARY KEY (id);


--
-- Name: custom_integrations custom_integrations_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.custom_integrations
    ADD CONSTRAINT custom_integrations_pkey PRIMARY KEY (id);


--
-- Name: evidence_controls evidence_controls_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence_controls
    ADD CONSTRAINT evidence_controls_pkey PRIMARY KEY (id);


--
-- Name: evidence evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_pkey PRIMARY KEY (id);


--
-- Name: frameworks frameworks_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.frameworks
    ADD CONSTRAINT frameworks_pkey PRIMARY KEY (id);


--
-- Name: integration_logs integration_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_logs
    ADD CONSTRAINT integration_logs_pkey PRIMARY KEY (id);


--
-- Name: integration_schedules integration_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_schedules
    ADD CONSTRAINT integration_schedules_pkey PRIMARY KEY (id);


--
-- Name: integration_templates integration_templates_name_key; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_templates
    ADD CONSTRAINT integration_templates_name_key UNIQUE (name);


--
-- Name: integration_templates integration_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_templates
    ADD CONSTRAINT integration_templates_pkey PRIMARY KEY (id);


--
-- Name: integrations integrations_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integrations
    ADD CONSTRAINT integrations_pkey PRIMARY KEY (id);


--
-- Name: report_generation_history report_generation_history_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_generation_history
    ADD CONSTRAINT report_generation_history_pkey PRIMARY KEY (id);


--
-- Name: report_templates report_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_templates
    ADD CONSTRAINT report_templates_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: risk_matrices risk_matrices_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risk_matrices
    ADD CONSTRAINT risk_matrices_pkey PRIMARY KEY (id);


--
-- Name: risk_scores risk_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risk_scores
    ADD CONSTRAINT risk_scores_pkey PRIMARY KEY (id);


--
-- Name: risks risks_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: scheduled_reports scheduled_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.scheduled_reports
    ADD CONSTRAINT scheduled_reports_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: task_comments task_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_comments
    ADD CONSTRAINT task_comments_pkey PRIMARY KEY (id);


--
-- Name: task_evidence task_evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_evidence
    ADD CONSTRAINT task_evidence_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: threat_intel_data threat_intel_data_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.threat_intel_data
    ADD CONSTRAINT threat_intel_data_pkey PRIMARY KEY (id);


--
-- Name: settings uq_setting_category_key; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT uq_setting_category_key UNIQUE (category, key);


--
-- Name: user_activities user_activities_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vulnerability_data vulnerability_data_pkey; Type: CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.vulnerability_data
    ADD CONSTRAINT vulnerability_data_pkey PRIMARY KEY (id);


--
-- Name: idx_settings_unique_category_key; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE UNIQUE INDEX idx_settings_unique_category_key ON public.settings USING btree (category, key);


--
-- Name: idx_user_roles_unique; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE UNIQUE INDEX idx_user_roles_unique ON public.user_roles USING btree (user_id, role_id);


--
-- Name: ix_assessment_controls_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_assessment_controls_id ON public.assessment_controls USING btree (id);


--
-- Name: ix_assessments_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_assessments_id ON public.assessments USING btree (id);


--
-- Name: ix_asset_categories_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_asset_categories_id ON public.asset_categories USING btree (id);


--
-- Name: ix_assets_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_assets_id ON public.assets USING btree (id);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_control_mappings_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_control_mappings_id ON public.control_mappings USING btree (id);


--
-- Name: ix_controls_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_controls_id ON public.controls USING btree (id);


--
-- Name: ix_custom_integrations_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_custom_integrations_id ON public.custom_integrations USING btree (id);


--
-- Name: ix_evidence_controls_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_evidence_controls_id ON public.evidence_controls USING btree (id);


--
-- Name: ix_evidence_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_evidence_id ON public.evidence USING btree (id);


--
-- Name: ix_frameworks_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_frameworks_id ON public.frameworks USING btree (id);


--
-- Name: ix_integration_logs_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_integration_logs_id ON public.integration_logs USING btree (id);


--
-- Name: ix_integration_schedules_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_integration_schedules_id ON public.integration_schedules USING btree (id);


--
-- Name: ix_integration_templates_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_integration_templates_id ON public.integration_templates USING btree (id);


--
-- Name: ix_integrations_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_integrations_id ON public.integrations USING btree (id);


--
-- Name: ix_report_generation_history_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_report_generation_history_id ON public.report_generation_history USING btree (id);


--
-- Name: ix_report_templates_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_report_templates_id ON public.report_templates USING btree (id);


--
-- Name: ix_reports_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_reports_id ON public.reports USING btree (id);


--
-- Name: ix_risk_matrices_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_risk_matrices_id ON public.risk_matrices USING btree (id);


--
-- Name: ix_risk_scores_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_risk_scores_id ON public.risk_scores USING btree (id);


--
-- Name: ix_risks_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_risks_id ON public.risks USING btree (id);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_scheduled_reports_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_scheduled_reports_id ON public.scheduled_reports USING btree (id);


--
-- Name: ix_settings_category; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_settings_category ON public.settings USING btree (category);


--
-- Name: ix_settings_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_settings_id ON public.settings USING btree (id);


--
-- Name: ix_settings_key; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_settings_key ON public.settings USING btree (key);


--
-- Name: ix_task_comments_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_task_comments_id ON public.task_comments USING btree (id);


--
-- Name: ix_task_evidence_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_task_evidence_id ON public.task_evidence USING btree (id);


--
-- Name: ix_tasks_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_tasks_id ON public.tasks USING btree (id);


--
-- Name: ix_threat_intel_data_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_threat_intel_data_id ON public.threat_intel_data USING btree (id);


--
-- Name: ix_user_activities_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_user_activities_id ON public.user_activities USING btree (id);


--
-- Name: ix_user_roles_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_user_roles_id ON public.user_roles USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_vulnerability_data_id; Type: INDEX; Schema: public; Owner: aegis_user
--

CREATE INDEX ix_vulnerability_data_id ON public.vulnerability_data USING btree (id);


--
-- Name: assessment_controls assessment_controls_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessment_controls
    ADD CONSTRAINT assessment_controls_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.assessments(id);


--
-- Name: assessment_controls assessment_controls_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessment_controls
    ADD CONSTRAINT assessment_controls_control_id_fkey FOREIGN KEY (control_id) REFERENCES public.controls(id);


--
-- Name: assessment_controls assessment_controls_reviewed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessment_controls
    ADD CONSTRAINT assessment_controls_reviewed_by_id_fkey FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id);


--
-- Name: assessments assessments_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id);


--
-- Name: assessments assessments_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: assessments assessments_framework_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_framework_id_fkey FOREIGN KEY (framework_id) REFERENCES public.frameworks(id);


--
-- Name: assessments assessments_lead_assessor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_lead_assessor_id_fkey FOREIGN KEY (lead_assessor_id) REFERENCES public.users(id);


--
-- Name: assets assets_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.asset_categories(id);


--
-- Name: assets assets_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: assets assets_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: control_mappings control_mappings_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.control_mappings
    ADD CONSTRAINT control_mappings_control_id_fkey FOREIGN KEY (control_id) REFERENCES public.controls(id);


--
-- Name: controls controls_framework_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.controls
    ADD CONSTRAINT controls_framework_id_fkey FOREIGN KEY (framework_id) REFERENCES public.frameworks(id);


--
-- Name: controls controls_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.controls
    ADD CONSTRAINT controls_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.controls(id);


--
-- Name: custom_integrations custom_integrations_integration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.custom_integrations
    ADD CONSTRAINT custom_integrations_integration_id_fkey FOREIGN KEY (integration_id) REFERENCES public.integrations(id);


--
-- Name: custom_integrations custom_integrations_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.custom_integrations
    ADD CONSTRAINT custom_integrations_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.integration_templates(id);


--
-- Name: evidence_controls evidence_controls_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence_controls
    ADD CONSTRAINT evidence_controls_control_id_fkey FOREIGN KEY (control_id) REFERENCES public.controls(id);


--
-- Name: evidence_controls evidence_controls_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence_controls
    ADD CONSTRAINT evidence_controls_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: evidence_controls evidence_controls_evidence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence_controls
    ADD CONSTRAINT evidence_controls_evidence_id_fkey FOREIGN KEY (evidence_id) REFERENCES public.evidence(id);


--
-- Name: evidence evidence_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: evidence evidence_previous_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_previous_version_id_fkey FOREIGN KEY (previous_version_id) REFERENCES public.evidence(id);


--
-- Name: evidence evidence_reviewed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_reviewed_by_id_fkey FOREIGN KEY (reviewed_by_id) REFERENCES public.users(id);


--
-- Name: evidence evidence_uploaded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_uploaded_by_id_fkey FOREIGN KEY (uploaded_by_id) REFERENCES public.users(id);


--
-- Name: integration_logs integration_logs_integration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_logs
    ADD CONSTRAINT integration_logs_integration_id_fkey FOREIGN KEY (integration_id) REFERENCES public.integrations(id);


--
-- Name: integration_schedules integration_schedules_integration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_schedules
    ADD CONSTRAINT integration_schedules_integration_id_fkey FOREIGN KEY (integration_id) REFERENCES public.integrations(id);


--
-- Name: integration_templates integration_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integration_templates
    ADD CONSTRAINT integration_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: integrations integrations_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.integrations
    ADD CONSTRAINT integrations_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: report_generation_history report_generation_history_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_generation_history
    ADD CONSTRAINT report_generation_history_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.reports(id);


--
-- Name: report_generation_history report_generation_history_scheduled_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_generation_history
    ADD CONSTRAINT report_generation_history_scheduled_report_id_fkey FOREIGN KEY (scheduled_report_id) REFERENCES public.scheduled_reports(id);


--
-- Name: report_generation_history report_generation_history_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_generation_history
    ADD CONSTRAINT report_generation_history_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(id);


--
-- Name: report_generation_history report_generation_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_generation_history
    ADD CONSTRAINT report_generation_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: report_templates report_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.report_templates
    ADD CONSTRAINT report_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: reports reports_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: reports reports_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(id);


--
-- Name: risk_scores risk_scores_risk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risk_scores
    ADD CONSTRAINT risk_scores_risk_id_fkey FOREIGN KEY (risk_id) REFERENCES public.risks(id);


--
-- Name: risk_scores risk_scores_scored_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risk_scores
    ADD CONSTRAINT risk_scores_scored_by_fkey FOREIGN KEY (scored_by) REFERENCES public.users(id);


--
-- Name: risks risks_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id);


--
-- Name: risks risks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: risks risks_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: risks risks_risk_matrix_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_risk_matrix_id_fkey FOREIGN KEY (risk_matrix_id) REFERENCES public.risk_matrices(id);


--
-- Name: scheduled_reports scheduled_reports_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.scheduled_reports
    ADD CONSTRAINT scheduled_reports_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: scheduled_reports scheduled_reports_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.scheduled_reports
    ADD CONSTRAINT scheduled_reports_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(id);


--
-- Name: task_comments task_comments_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_comments
    ADD CONSTRAINT task_comments_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_comments task_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_comments
    ADD CONSTRAINT task_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: task_evidence task_evidence_evidence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_evidence
    ADD CONSTRAINT task_evidence_evidence_id_fkey FOREIGN KEY (evidence_id) REFERENCES public.evidence(id);


--
-- Name: task_evidence task_evidence_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.task_evidence
    ADD CONSTRAINT task_evidence_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: tasks tasks_approved_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_approved_by_id_fkey FOREIGN KEY (approved_by_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id);


--
-- Name: tasks tasks_assigned_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_to_id_fkey FOREIGN KEY (assigned_to_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_progress_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_progress_updated_by_id_fkey FOREIGN KEY (progress_updated_by_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_risk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_risk_id_fkey FOREIGN KEY (risk_id) REFERENCES public.risks(id);


--
-- Name: threat_intel_data threat_intel_data_integration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.threat_intel_data
    ADD CONSTRAINT threat_intel_data_integration_id_fkey FOREIGN KEY (integration_id) REFERENCES public.integrations(id);


--
-- Name: user_activities user_activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: vulnerability_data vulnerability_data_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.vulnerability_data
    ADD CONSTRAINT vulnerability_data_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id);


--
-- Name: vulnerability_data vulnerability_data_integration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: aegis_user
--

ALTER TABLE ONLY public.vulnerability_data
    ADD CONSTRAINT vulnerability_data_integration_id_fkey FOREIGN KEY (integration_id) REFERENCES public.integrations(id);


--
-- PostgreSQL database dump complete
--

