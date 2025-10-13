--
-- PostgreSQL database dump
--

\restrict ScV57X0hlbucbTmOQ0WOvg1Fwlc88nFfReYvLAJIRj4LpeAXqGb5EVsv2Gxji57

-- Dumped from database version 17.6 (Debian 17.6-1.pgdg13+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: approvalstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.approvalstatus AS ENUM (
    'pending',
    'approved',
    'rejected',
    'escalated'
);


ALTER TYPE public.approvalstatus OWNER TO postgres;

--
-- Name: lineitemtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.lineitemtype AS ENUM (
    'product',
    'service',
    'discount',
    'shipping',
    'tax',
    'misc'
);


ALTER TYPE public.lineitemtype OWNER TO postgres;

--
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.paymentstatus AS ENUM (
    'pending',
    'authorized',
    'partially_paid',
    'paid',
    'overdue',
    'refunded',
    'cancelled'
);


ALTER TYPE public.paymentstatus OWNER TO postgres;

--
-- Name: quotestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.quotestatus AS ENUM (
    'draft',
    'pending_approval',
    'approved',
    'sent',
    'accepted',
    'rejected',
    'expired',
    'converted',
    'cancelled'
);


ALTER TYPE public.quotestatus OWNER TO postgres;

--
-- Name: salestransactionstate; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.salestransactionstate AS ENUM (
    'draft',
    'quote_pending_approval',
    'quote_approved',
    'quote_sent',
    'quote_accepted',
    'quote_rejected',
    'quote_expired',
    'order_pending',
    'order_confirmed',
    'order_in_production',
    'order_ready_to_ship',
    'order_partially_shipped',
    'order_shipped',
    'order_delivered',
    'order_completed',
    'order_cancelled',
    'order_on_hold'
);


ALTER TYPE public.salestransactionstate OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: quote_approvals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quote_approvals (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    quote_id integer NOT NULL,
    approval_level integer DEFAULT 1 NOT NULL,
    requested_by_user_id integer NOT NULL,
    assigned_to_user_id integer NOT NULL,
    request_date timestamp without time zone NOT NULL,
    request_reason text,
    urgency_level character varying(20) DEFAULT 'normal'::character varying NOT NULL,
    status public.approvalstatus DEFAULT 'pending'::public.approvalstatus NOT NULL,
    response_date timestamp without time zone,
    response_by_user_id integer,
    response_notes text,
    escalated_date timestamp without time zone,
    escalated_to_user_id integer,
    escalation_reason character varying(255),
    due_date timestamp without time zone,
    sla_hours integer DEFAULT 24 NOT NULL,
    discount_percentage numeric(5,2),
    quote_total numeric(15,2),
    margin_percentage numeric(5,2),
    attachments json,
    approval_notes text,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.quote_approvals OWNER TO postgres;

--
-- Name: quote_approvals_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quote_approvals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quote_approvals_id_seq OWNER TO postgres;

--
-- Name: quote_approvals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quote_approvals_id_seq OWNED BY public.quote_approvals.id;


--
-- Name: quote_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quote_versions (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    quote_id integer NOT NULL,
    version_number integer NOT NULL,
    created_by_user_id integer NOT NULL,
    change_reason character varying(255),
    change_summary text,
    quote_data json NOT NULL,
    line_items_data json,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.quote_versions OWNER TO postgres;

--
-- Name: quote_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quote_versions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quote_versions_id_seq OWNER TO postgres;

--
-- Name: quote_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quote_versions_id_seq OWNED BY public.quote_versions.id;


--
-- Name: sales_quote_line_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales_quote_line_items (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    quote_id integer NOT NULL,
    line_number integer NOT NULL,
    line_type public.lineitemtype DEFAULT 'product'::public.lineitemtype NOT NULL,
    product_id integer,
    product_variant_id integer,
    item_code character varying(100),
    item_name character varying(255) NOT NULL,
    description text,
    quantity numeric(15,4) DEFAULT 1.0000 NOT NULL,
    unit_of_measure character varying(50) DEFAULT 'each'::character varying NOT NULL,
    unit_price numeric(15,4) NOT NULL,
    list_price numeric(15,4),
    unit_cost numeric(15,4),
    discount_percentage numeric(5,2) DEFAULT 0.00 NOT NULL,
    discount_amount numeric(15,2) DEFAULT 0.00 NOT NULL,
    line_total numeric(15,2) NOT NULL,
    line_cost numeric(15,2),
    tax_percentage numeric(5,2) DEFAULT 0.00 NOT NULL,
    tax_amount numeric(15,2) DEFAULT 0.00 NOT NULL,
    tax_code character varying(50),
    specifications json,
    custom_options json,
    lead_time_days integer,
    delivery_date timestamp without time zone,
    price_rule_id integer,
    promotion_id integer,
    is_active boolean DEFAULT true NOT NULL,
    notes text,
    custom_attributes json
);


ALTER TABLE public.sales_quote_line_items OWNER TO postgres;

--
-- Name: sales_quote_line_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sales_quote_line_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_quote_line_items_id_seq OWNER TO postgres;

--
-- Name: sales_quote_line_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sales_quote_line_items_id_seq OWNED BY public.sales_quote_line_items.id;


--
-- Name: sales_quotes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales_quotes (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    quote_number character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    customer_id integer NOT NULL,
    opportunity_id integer,
    status public.quotestatus DEFAULT 'draft'::public.quotestatus NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    subtotal numeric(15,2) DEFAULT 0.00 NOT NULL,
    discount_amount numeric(15,2) DEFAULT 0.00 NOT NULL,
    tax_amount numeric(15,2) DEFAULT 0.00 NOT NULL,
    shipping_amount numeric(15,2) DEFAULT 0.00 NOT NULL,
    total_amount numeric(15,2) DEFAULT 0.00 NOT NULL,
    currency_code character varying(3) DEFAULT 'USD'::character varying NOT NULL,
    overall_discount_percentage numeric(5,2) DEFAULT 0.00 NOT NULL,
    margin_percentage numeric(5,2),
    total_cost numeric(15,2),
    valid_from timestamp without time zone NOT NULL,
    valid_until timestamp without time zone NOT NULL,
    payment_terms_days integer DEFAULT 30 NOT NULL,
    delivery_terms character varying(255),
    prepared_by_user_id integer NOT NULL,
    approved_by_user_id integer,
    sent_date timestamp without time zone,
    sent_by_user_id integer,
    customer_response_date timestamp without time zone,
    customer_response_notes text,
    rejection_reason character varying(255),
    requires_approval boolean DEFAULT false NOT NULL,
    approval_threshold_amount numeric(15,2),
    approval_notes text,
    converted_to_order_id integer,
    converted_date timestamp without time zone,
    converted_by_user_id integer,
    template_id integer,
    document_url character varying(500),
    pdf_generated boolean DEFAULT false NOT NULL,
    email_sent_count integer DEFAULT 0 NOT NULL,
    last_email_sent timestamp without time zone,
    viewed_by_customer boolean DEFAULT false NOT NULL,
    first_viewed_date timestamp without time zone,
    last_viewed_date timestamp without time zone,
    internal_notes text,
    terms_and_conditions text,
    custom_fields json,
    tags json,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.sales_quotes OWNER TO postgres;

--
-- Name: sales_quotes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sales_quotes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_quotes_id_seq OWNER TO postgres;

--
-- Name: sales_quotes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sales_quotes_id_seq OWNED BY public.sales_quotes.id;


--
-- Name: sales_transaction_line_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales_transaction_line_items (
    id integer NOT NULL,
    company_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    created_by_user_id integer,
    updated_by_user_id integer,
    transaction_id integer NOT NULL,
    line_number integer NOT NULL,
    line_type public.lineitemtype NOT NULL,
    product_id integer,
    product_variant_id integer,
    item_code character varying(100),
    item_name character varying(255) NOT NULL,
    description text,
    quantity_ordered numeric(15,4) NOT NULL,
    quantity_shipped numeric(15,4) NOT NULL,
    quantity_cancelled numeric(15,4) NOT NULL,
    quantity_backordered numeric(15,4) NOT NULL,
    unit_of_measure character varying(50) NOT NULL,
    unit_price numeric(15,4) NOT NULL,
    unit_cost numeric(15,4),
    discount_percentage numeric(5,2) NOT NULL,
    discount_amount numeric(15,2) NOT NULL,
    line_total numeric(15,2) NOT NULL,
    line_cost numeric(15,2),
    tax_percentage numeric(5,2) NOT NULL,
    tax_amount numeric(15,2) NOT NULL,
    tax_code character varying(50),
    warehouse_id integer,
    reserved_quantity numeric(15,4) NOT NULL,
    allocated_quantity numeric(15,4) NOT NULL,
    required_date timestamp without time zone,
    promised_date timestamp without time zone,
    shipped_date timestamp without time zone,
    specifications json,
    custom_options json,
    is_backordered boolean NOT NULL,
    is_dropship boolean NOT NULL,
    requires_special_handling boolean NOT NULL,
    notes text,
    custom_attributes json,
    is_active boolean NOT NULL,
    framework_version character varying(50)
);


ALTER TABLE public.sales_transaction_line_items OWNER TO postgres;

--
-- Name: sales_transaction_line_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sales_transaction_line_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_transaction_line_items_id_seq OWNER TO postgres;

--
-- Name: sales_transaction_line_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sales_transaction_line_items_id_seq OWNED BY public.sales_transaction_line_items.id;


--
-- Name: sales_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales_transactions (
    id integer NOT NULL,
    company_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    created_by_user_id integer,
    updated_by_user_id integer,
    transaction_number character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    customer_id integer NOT NULL,
    opportunity_id integer,
    state public.salestransactionstate NOT NULL,
    version integer NOT NULL,
    subtotal numeric(15,2) NOT NULL,
    discount_amount numeric(15,2) NOT NULL,
    tax_amount numeric(15,2) NOT NULL,
    shipping_amount numeric(15,2) NOT NULL,
    total_amount numeric(15,2) NOT NULL,
    currency_code character varying(3) NOT NULL,
    overall_discount_percentage numeric(5,2) NOT NULL,
    margin_percentage numeric(5,2),
    total_cost numeric(15,2),
    valid_from timestamp without time zone NOT NULL,
    valid_until timestamp without time zone,
    payment_terms_days integer NOT NULL,
    delivery_terms character varying(255),
    prepared_by_user_id integer NOT NULL,
    approved_by_user_id integer,
    sent_date timestamp without time zone,
    sent_by_user_id integer,
    customer_response_date timestamp without time zone,
    customer_response_notes text,
    rejection_reason character varying(255),
    requires_approval boolean NOT NULL,
    approval_threshold_amount numeric(15,2),
    approval_notes text,
    order_date timestamp without time zone,
    required_date timestamp without time zone,
    promised_date timestamp without time zone,
    shipped_date timestamp without time zone,
    delivered_date timestamp without time zone,
    due_date timestamp without time zone,
    paid_amount numeric(15,2) NOT NULL,
    outstanding_amount numeric(15,2) NOT NULL,
    payment_status public.paymentstatus NOT NULL,
    source_channel character varying(50),
    sales_rep_user_id integer,
    shipping_method character varying(100),
    carrier_name character varying(100),
    tracking_number character varying(255),
    billing_address json,
    shipping_address json,
    is_priority boolean NOT NULL,
    is_dropship boolean NOT NULL,
    is_backorder_allowed boolean NOT NULL,
    customer_po_number character varying(100),
    special_instructions text,
    internal_notes text,
    items_shipped integer NOT NULL,
    items_remaining integer NOT NULL,
    shipment_count integer NOT NULL,
    template_id integer,
    document_url character varying(500),
    pdf_generated boolean NOT NULL,
    email_sent_count integer NOT NULL,
    last_email_sent timestamp without time zone,
    viewed_by_customer boolean NOT NULL,
    first_viewed_date timestamp without time zone,
    last_viewed_date timestamp without time zone,
    terms_and_conditions text,
    custom_fields json,
    tags json,
    is_active boolean NOT NULL,
    framework_version character varying(50),
    transaction_date timestamp without time zone,
    discount_code character varying(50),
    discount_reason character varying(255),
    discount numeric(15,2),
    tax numeric(15,2),
    total numeric(15,2),
    shipping numeric(15,2)
);


ALTER TABLE public.sales_transactions OWNER TO postgres;

--
-- Name: sales_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sales_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_transactions_id_seq OWNER TO postgres;

--
-- Name: sales_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sales_transactions_id_seq OWNED BY public.sales_transactions.id;


--
-- Name: quote_approvals id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_approvals ALTER COLUMN id SET DEFAULT nextval('public.quote_approvals_id_seq'::regclass);


--
-- Name: quote_versions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_versions ALTER COLUMN id SET DEFAULT nextval('public.quote_versions_id_seq'::regclass);


--
-- Name: sales_quote_line_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_quote_line_items ALTER COLUMN id SET DEFAULT nextval('public.sales_quote_line_items_id_seq'::regclass);


--
-- Name: sales_quotes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_quotes ALTER COLUMN id SET DEFAULT nextval('public.sales_quotes_id_seq'::regclass);


--
-- Name: sales_transaction_line_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_transaction_line_items ALTER COLUMN id SET DEFAULT nextval('public.sales_transaction_line_items_id_seq'::regclass);


--
-- Name: sales_transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_transactions ALTER COLUMN id SET DEFAULT nextval('public.sales_transactions_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
20251011_180000
\.


--
-- Data for Name: quote_approvals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quote_approvals (id, created_at, updated_at, company_id, framework_version, quote_id, approval_level, requested_by_user_id, assigned_to_user_id, request_date, request_reason, urgency_level, status, response_date, response_by_user_id, response_notes, escalated_date, escalated_to_user_id, escalation_reason, due_date, sla_hours, discount_percentage, quote_total, margin_percentage, attachments, approval_notes, is_active) FROM stdin;
\.


--
-- Data for Name: quote_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quote_versions (id, created_at, updated_at, company_id, framework_version, quote_id, version_number, created_by_user_id, change_reason, change_summary, quote_data, line_items_data, is_active) FROM stdin;
\.


--
-- Data for Name: sales_quote_line_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sales_quote_line_items (id, created_at, updated_at, company_id, framework_version, quote_id, line_number, line_type, product_id, product_variant_id, item_code, item_name, description, quantity, unit_of_measure, unit_price, list_price, unit_cost, discount_percentage, discount_amount, line_total, line_cost, tax_percentage, tax_amount, tax_code, specifications, custom_options, lead_time_days, delivery_date, price_rule_id, promotion_id, is_active, notes, custom_attributes) FROM stdin;
\.


--
-- Data for Name: sales_quotes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sales_quotes (id, created_at, updated_at, company_id, framework_version, quote_number, title, description, customer_id, opportunity_id, status, version, subtotal, discount_amount, tax_amount, shipping_amount, total_amount, currency_code, overall_discount_percentage, margin_percentage, total_cost, valid_from, valid_until, payment_terms_days, delivery_terms, prepared_by_user_id, approved_by_user_id, sent_date, sent_by_user_id, customer_response_date, customer_response_notes, rejection_reason, requires_approval, approval_threshold_amount, approval_notes, converted_to_order_id, converted_date, converted_by_user_id, template_id, document_url, pdf_generated, email_sent_count, last_email_sent, viewed_by_customer, first_viewed_date, last_viewed_date, internal_notes, terms_and_conditions, custom_fields, tags, is_active) FROM stdin;
\.


--
-- Data for Name: sales_transaction_line_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sales_transaction_line_items (id, company_id, created_at, updated_at, created_by_user_id, updated_by_user_id, transaction_id, line_number, line_type, product_id, product_variant_id, item_code, item_name, description, quantity_ordered, quantity_shipped, quantity_cancelled, quantity_backordered, unit_of_measure, unit_price, unit_cost, discount_percentage, discount_amount, line_total, line_cost, tax_percentage, tax_amount, tax_code, warehouse_id, reserved_quantity, allocated_quantity, required_date, promised_date, shipped_date, specifications, custom_options, is_backordered, is_dropship, requires_special_handling, notes, custom_attributes, is_active, framework_version) FROM stdin;
2	1	2025-09-25 23:16:31.233752	2025-09-25 23:16:31.23376	\N	\N	8	1	product	\N	\N	TEST-001	Test Product	\N	2.0000	0.0000	0.0000	0.0000	each	50.0000	\N	0.00	0.00	100.00	\N	0.00	0.00	\N	\N	0.0000	0.0000	\N	\N	\N	\N	\N	f	f	f	\N	\N	t	1.0.0
3	1	2025-09-30 08:03:42.246853	2025-09-30 08:03:42.246859	\N	\N	9	1	product	2001	\N	WIDGET-A	Premium Widget A	High-quality premium widget	2.0000	0.0000	0.0000	0.0000	each	125.0000	\N	0.00	0.00	250.00	\N	0.00	0.00	\N	\N	0.0000	0.0000	\N	\N	\N	\N	\N	f	f	f	\N	\N	t	1.0.0
4	1	2025-09-30 08:03:42.276373	2025-09-30 08:03:42.276381	\N	\N	9	2	product	2002	\N	GADGET-B	Advanced Gadget B	Advanced multi-purpose gadget	1.0000	0.0000	0.0000	0.0000	each	250.0000	\N	0.00	0.00	250.00	\N	0.00	0.00	\N	\N	0.0000	0.0000	\N	\N	\N	\N	\N	f	f	f	\N	\N	t	1.0.0
\.


--
-- Data for Name: sales_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sales_transactions (id, company_id, created_at, updated_at, created_by_user_id, updated_by_user_id, transaction_number, title, description, customer_id, opportunity_id, state, version, subtotal, discount_amount, tax_amount, shipping_amount, total_amount, currency_code, overall_discount_percentage, margin_percentage, total_cost, valid_from, valid_until, payment_terms_days, delivery_terms, prepared_by_user_id, approved_by_user_id, sent_date, sent_by_user_id, customer_response_date, customer_response_notes, rejection_reason, requires_approval, approval_threshold_amount, approval_notes, order_date, required_date, promised_date, shipped_date, delivered_date, due_date, paid_amount, outstanding_amount, payment_status, source_channel, sales_rep_user_id, shipping_method, carrier_name, tracking_number, billing_address, shipping_address, is_priority, is_dropship, is_backorder_allowed, customer_po_number, special_instructions, internal_notes, items_shipped, items_remaining, shipment_count, template_id, document_url, pdf_generated, email_sent_count, last_email_sent, viewed_by_customer, first_viewed_date, last_viewed_date, terms_and_conditions, custom_fields, tags, is_active, framework_version, transaction_date, discount_code, discount_reason, discount, tax, total, shipping) FROM stdin;
17	1	2025-09-30 08:49:19.202164	2025-10-01 22:37:50.682148	\N	1	TXN-APPROVED-1759193359	Approved Transaction	\N	1001	\N	quote_sent	1	200.00	0.00	16.00	0.00	216.00	USD	0.00	\N	\N	2025-09-30 08:49:19.20069	2025-10-30 08:49:19.200702	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
18	1	2025-09-30 08:49:19.218054	2025-10-01 22:44:01.381723	\N	1	TXN-SENT-1759193359	Sent Transaction	\N	1001	\N	quote_accepted	1	300.00	0.00	24.00	0.00	324.00	USD	0.00	\N	\N	2025-09-30 08:49:19.216483	2025-10-30 08:49:19.216491	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
20	1	2025-09-30 08:50:22.691148	2025-10-02 07:24:35.855137	\N	1	TXN-APPROVED-1759193422	Approved Transaction	\N	1001	\N	order_delivered	1	200.00	0.00	16.00	0.00	216.00	USD	0.00	\N	\N	2025-09-30 08:50:22.68932	2025-10-30 08:50:22.689328	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
15	1	2025-09-30 08:49:05.361334	2025-09-30 08:49:05.361347	\N	\N	TXN-SENT-1759193345	Sent Transaction	\N	1001	\N	quote_sent	1	300.00	0.00	24.00	0.00	324.00	USD	0.00	\N	\N	2025-09-30 08:49:05.359624	2025-10-30 08:49:05.359633	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
16	1	2025-09-30 08:49:19.186548	2025-09-30 08:49:19.186555	\N	\N	TXN-DRAFT-1759193359	Draft Transaction	\N	1001	\N	draft	1	100.00	0.00	8.00	0.00	108.00	USD	0.00	\N	\N	2025-09-30 08:49:19.184811	2025-10-30 08:49:19.18482	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
22	1	2025-09-30 08:56:17.762153	2025-10-11 23:59:15.339206	\N	1	TXN-APPROVED-1759193777	Approved Transaction	\N	3	\N	order_completed	1	900.00	0.00	16.00	0.00	216.00	USD	0.00	\N	\N	2025-09-30 08:56:17.760558	2025-10-30 08:56:17.76057	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	2025-09-30 00:00:00	\N	\N	\N	\N	\N	\N
6	1	2025-09-20 09:33:00.300218	2025-09-26 04:12:23.09483	\N	1	TXN-TEST-003	Test Transaction	\N	1	\N	draft	1	100.00	0.00	8.00	0.00	108.00	USD	0.00	\N	\N	2025-09-20 09:33:00.300204	\N	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
8	1	2025-09-20 09:55:43.227388	2025-09-30 05:36:02.152831	\N	1	TXN-2025-011	001	Updated description for testing persistence	3	\N	quote_approved	1	9000.00	75.00	80.00	0.00	1005.00	USD	0.00	\N	\N	2025-09-20 09:55:43.219121	2026-09-20 09:55:43.219141	30	FBO	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	authorized	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	notes	0	0	0	\N	\N	f	0	\N	f	\N	\N	term	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
7	1	2025-09-20 09:33:15.389464	2025-09-30 07:17:33.758196	\N	1	TXN-2025-010	API Test Transaction	descdsd	2	\N	draft	1	1000.00	0.00	8.00	0.00	108.00	USD	0.00	\N	\N	2025-09-20 09:33:15.320658	2025-10-20 09:33:15.320675	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
9	1	2025-09-30 08:03:42.1913	2025-09-30 08:08:20.347965	\N	1	TXN-LI-TEST-1759190622	Line Items Test Transaction	Test transaction to verify line items inclusion	1	\N	draft	1	500.00	0.00	40.00	0.00	540.00	USD	0.00	\N	\N	2025-09-30 08:03:42.175205	2026-09-30 08:03:42.175214	30	FOB	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	okoo	0	0	0	\N	\N	f	0	\N	f	\N	\N	okoko	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
10	1	2025-09-30 08:48:26.345493	2025-09-30 08:48:26.3455	\N	\N	TXN-DRAFT-1759193306	Draft Transaction	\N	1001	\N	draft	1	100.00	0.00	8.00	0.00	108.00	USD	0.00	\N	\N	2025-09-30 08:48:26.337749	2025-10-30 08:48:26.337757	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
11	1	2025-09-30 08:48:26.366135	2025-09-30 08:48:26.366141	\N	\N	TXN-APPROVED-1759193306	Approved Transaction	\N	1001	\N	quote_approved	1	200.00	0.00	16.00	0.00	216.00	USD	0.00	\N	\N	2025-09-30 08:48:26.363875	2025-10-30 08:48:26.363883	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
12	1	2025-09-30 08:48:26.381785	2025-09-30 08:48:26.381791	\N	\N	TXN-SENT-1759193306	Sent Transaction	\N	1001	\N	quote_sent	1	300.00	0.00	24.00	0.00	324.00	USD	0.00	\N	\N	2025-09-30 08:48:26.379763	2025-10-30 08:48:26.37977	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
13	1	2025-09-30 08:49:05.321276	2025-09-30 08:49:05.321286	\N	\N	TXN-DRAFT-1759193345	Draft Transaction	\N	1001	\N	draft	1	100.00	0.00	8.00	0.00	108.00	USD	0.00	\N	\N	2025-09-30 08:49:05.317423	2025-10-30 08:49:05.317463	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
14	1	2025-09-30 08:49:05.345762	2025-09-30 08:49:05.345769	\N	\N	TXN-APPROVED-1759193345	Approved Transaction	\N	1001	\N	quote_approved	1	200.00	0.00	16.00	0.00	216.00	USD	0.00	\N	\N	2025-09-30 08:49:05.343286	2025-10-30 08:49:05.343301	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
5	1	2025-09-20 01:22:08.088173	2025-10-01 10:35:25.828089	\N	1	TEST001	Test Transaction	\N	1	\N	quote_pending_approval	1	990.00	0.00	0.00	0.00	100.00	USD	0.00	\N	\N	2025-09-20 01:22:08.088173	\N	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
21	1	2025-09-30 08:56:17.742051	2025-10-01 21:11:13.63187	\N	1	TXN-DRAFT-1759193777	Draft Transaction00	\N	3	\N	order_in_production	1	100.00	0.00	8.00	0.00	108.00	USD	0.00	\N	\N	2025-09-30 08:56:17.737371	2025-10-30 08:56:17.737379	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
19	1	2025-09-30 08:50:22.677602	2025-10-01 21:16:42.494369	\N	1	TXN-DRAFT-1759193422	Draft Transaction	\N	1001	\N	order_shipped	1	100.00	0.00	8.00	0.00	108.00	USD	0.00	\N	\N	2025-09-30 08:50:22.675746	2025-10-30 08:50:22.675753	30	\N	1	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	0.00	0.00	pending	\N	\N	\N	\N	\N	\N	\N	f	f	t	\N	\N	\N	0	0	0	\N	\N	f	0	\N	f	\N	\N	\N	\N	\N	t	1.0.0	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Name: quote_approvals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quote_approvals_id_seq', 1, false);


--
-- Name: quote_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quote_versions_id_seq', 1, false);


--
-- Name: sales_quote_line_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sales_quote_line_items_id_seq', 1, false);


--
-- Name: sales_quotes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sales_quotes_id_seq', 1, false);


--
-- Name: sales_transaction_line_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sales_transaction_line_items_id_seq', 4, true);


--
-- Name: sales_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sales_transactions_id_seq', 22, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: quote_approvals quote_approvals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_approvals
    ADD CONSTRAINT quote_approvals_pkey PRIMARY KEY (id);


--
-- Name: quote_versions quote_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_versions
    ADD CONSTRAINT quote_versions_pkey PRIMARY KEY (id);


--
-- Name: sales_quote_line_items sales_quote_line_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_quote_line_items
    ADD CONSTRAINT sales_quote_line_items_pkey PRIMARY KEY (id);


--
-- Name: sales_quotes sales_quotes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_quotes
    ADD CONSTRAINT sales_quotes_pkey PRIMARY KEY (id);


--
-- Name: sales_transaction_line_items sales_transaction_line_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_transaction_line_items
    ADD CONSTRAINT sales_transaction_line_items_pkey PRIMARY KEY (id);


--
-- Name: sales_transactions sales_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_transactions
    ADD CONSTRAINT sales_transactions_pkey PRIMARY KEY (id);


--
-- Name: sales_transactions sales_transactions_transaction_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_transactions
    ADD CONSTRAINT sales_transactions_transaction_number_key UNIQUE (transaction_number);


--
-- Name: ix_quote_approvals_assigned_to_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_assigned_to_user_id ON public.quote_approvals USING btree (assigned_to_user_id);


--
-- Name: ix_quote_approvals_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_company_id ON public.quote_approvals USING btree (company_id);


--
-- Name: ix_quote_approvals_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_due_date ON public.quote_approvals USING btree (due_date);


--
-- Name: ix_quote_approvals_escalated_to_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_escalated_to_user_id ON public.quote_approvals USING btree (escalated_to_user_id);


--
-- Name: ix_quote_approvals_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_id ON public.quote_approvals USING btree (id);


--
-- Name: ix_quote_approvals_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_is_active ON public.quote_approvals USING btree (is_active);


--
-- Name: ix_quote_approvals_quote_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_quote_id ON public.quote_approvals USING btree (quote_id);


--
-- Name: ix_quote_approvals_request_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_request_date ON public.quote_approvals USING btree (request_date);


--
-- Name: ix_quote_approvals_requested_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_requested_by_user_id ON public.quote_approvals USING btree (requested_by_user_id);


--
-- Name: ix_quote_approvals_response_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_response_by_user_id ON public.quote_approvals USING btree (response_by_user_id);


--
-- Name: ix_quote_approvals_response_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_response_date ON public.quote_approvals USING btree (response_date);


--
-- Name: ix_quote_approvals_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_approvals_status ON public.quote_approvals USING btree (status);


--
-- Name: ix_quote_versions_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_versions_company_id ON public.quote_versions USING btree (company_id);


--
-- Name: ix_quote_versions_created_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_versions_created_by_user_id ON public.quote_versions USING btree (created_by_user_id);


--
-- Name: ix_quote_versions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_versions_id ON public.quote_versions USING btree (id);


--
-- Name: ix_quote_versions_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_versions_is_active ON public.quote_versions USING btree (is_active);


--
-- Name: ix_quote_versions_quote_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_versions_quote_id ON public.quote_versions USING btree (quote_id);


--
-- Name: ix_quote_versions_version_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quote_versions_version_number ON public.quote_versions USING btree (version_number);


--
-- Name: ix_sales_quote_line_items_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_company_id ON public.sales_quote_line_items USING btree (company_id);


--
-- Name: ix_sales_quote_line_items_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_id ON public.sales_quote_line_items USING btree (id);


--
-- Name: ix_sales_quote_line_items_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_is_active ON public.sales_quote_line_items USING btree (is_active);


--
-- Name: ix_sales_quote_line_items_item_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_item_code ON public.sales_quote_line_items USING btree (item_code);


--
-- Name: ix_sales_quote_line_items_line_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_line_type ON public.sales_quote_line_items USING btree (line_type);


--
-- Name: ix_sales_quote_line_items_price_rule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_price_rule_id ON public.sales_quote_line_items USING btree (price_rule_id);


--
-- Name: ix_sales_quote_line_items_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_product_id ON public.sales_quote_line_items USING btree (product_id);


--
-- Name: ix_sales_quote_line_items_product_variant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_product_variant_id ON public.sales_quote_line_items USING btree (product_variant_id);


--
-- Name: ix_sales_quote_line_items_promotion_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_promotion_id ON public.sales_quote_line_items USING btree (promotion_id);


--
-- Name: ix_sales_quote_line_items_quote_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quote_line_items_quote_id ON public.sales_quote_line_items USING btree (quote_id);


--
-- Name: ix_sales_quotes_approved_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_approved_by_user_id ON public.sales_quotes USING btree (approved_by_user_id);


--
-- Name: ix_sales_quotes_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_company_id ON public.sales_quotes USING btree (company_id);


--
-- Name: ix_sales_quotes_converted_to_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_converted_to_order_id ON public.sales_quotes USING btree (converted_to_order_id);


--
-- Name: ix_sales_quotes_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_customer_id ON public.sales_quotes USING btree (customer_id);


--
-- Name: ix_sales_quotes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_id ON public.sales_quotes USING btree (id);


--
-- Name: ix_sales_quotes_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_is_active ON public.sales_quotes USING btree (is_active);


--
-- Name: ix_sales_quotes_opportunity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_opportunity_id ON public.sales_quotes USING btree (opportunity_id);


--
-- Name: ix_sales_quotes_prepared_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_prepared_by_user_id ON public.sales_quotes USING btree (prepared_by_user_id);


--
-- Name: ix_sales_quotes_quote_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sales_quotes_quote_number ON public.sales_quotes USING btree (quote_number);


--
-- Name: ix_sales_quotes_sent_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_sent_by_user_id ON public.sales_quotes USING btree (sent_by_user_id);


--
-- Name: ix_sales_quotes_sent_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_sent_date ON public.sales_quotes USING btree (sent_date);


--
-- Name: ix_sales_quotes_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_status ON public.sales_quotes USING btree (status);


--
-- Name: ix_sales_quotes_valid_until; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_quotes_valid_until ON public.sales_quotes USING btree (valid_until);


--
-- Name: ix_sales_transaction_line_items_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_company_id ON public.sales_transaction_line_items USING btree (company_id);


--
-- Name: ix_sales_transaction_line_items_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_is_active ON public.sales_transaction_line_items USING btree (is_active);


--
-- Name: ix_sales_transaction_line_items_item_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_item_code ON public.sales_transaction_line_items USING btree (item_code);


--
-- Name: ix_sales_transaction_line_items_line_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_line_type ON public.sales_transaction_line_items USING btree (line_type);


--
-- Name: ix_sales_transaction_line_items_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_product_id ON public.sales_transaction_line_items USING btree (product_id);


--
-- Name: ix_sales_transaction_line_items_product_variant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_product_variant_id ON public.sales_transaction_line_items USING btree (product_variant_id);


--
-- Name: ix_sales_transaction_line_items_promised_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_promised_date ON public.sales_transaction_line_items USING btree (promised_date);


--
-- Name: ix_sales_transaction_line_items_required_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_required_date ON public.sales_transaction_line_items USING btree (required_date);


--
-- Name: ix_sales_transaction_line_items_shipped_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_shipped_date ON public.sales_transaction_line_items USING btree (shipped_date);


--
-- Name: ix_sales_transaction_line_items_transaction_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_transaction_id ON public.sales_transaction_line_items USING btree (transaction_id);


--
-- Name: ix_sales_transaction_line_items_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transaction_line_items_warehouse_id ON public.sales_transaction_line_items USING btree (warehouse_id);


--
-- Name: ix_sales_transactions_approved_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_approved_by_user_id ON public.sales_transactions USING btree (approved_by_user_id);


--
-- Name: ix_sales_transactions_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_company_id ON public.sales_transactions USING btree (company_id);


--
-- Name: ix_sales_transactions_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_customer_id ON public.sales_transactions USING btree (customer_id);


--
-- Name: ix_sales_transactions_customer_po_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_customer_po_number ON public.sales_transactions USING btree (customer_po_number);


--
-- Name: ix_sales_transactions_delivered_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_delivered_date ON public.sales_transactions USING btree (delivered_date);


--
-- Name: ix_sales_transactions_discount_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_discount_code ON public.sales_transactions USING btree (discount_code);


--
-- Name: ix_sales_transactions_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_due_date ON public.sales_transactions USING btree (due_date);


--
-- Name: ix_sales_transactions_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_is_active ON public.sales_transactions USING btree (is_active);


--
-- Name: ix_sales_transactions_opportunity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_opportunity_id ON public.sales_transactions USING btree (opportunity_id);


--
-- Name: ix_sales_transactions_order_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_order_date ON public.sales_transactions USING btree (order_date);


--
-- Name: ix_sales_transactions_payment_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_payment_status ON public.sales_transactions USING btree (payment_status);


--
-- Name: ix_sales_transactions_prepared_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_prepared_by_user_id ON public.sales_transactions USING btree (prepared_by_user_id);


--
-- Name: ix_sales_transactions_promised_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_promised_date ON public.sales_transactions USING btree (promised_date);


--
-- Name: ix_sales_transactions_required_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_required_date ON public.sales_transactions USING btree (required_date);


--
-- Name: ix_sales_transactions_sales_rep_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_sales_rep_user_id ON public.sales_transactions USING btree (sales_rep_user_id);


--
-- Name: ix_sales_transactions_sent_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_sent_by_user_id ON public.sales_transactions USING btree (sent_by_user_id);


--
-- Name: ix_sales_transactions_sent_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_sent_date ON public.sales_transactions USING btree (sent_date);


--
-- Name: ix_sales_transactions_shipped_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_shipped_date ON public.sales_transactions USING btree (shipped_date);


--
-- Name: ix_sales_transactions_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_state ON public.sales_transactions USING btree (state);


--
-- Name: ix_sales_transactions_tracking_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_tracking_number ON public.sales_transactions USING btree (tracking_number);


--
-- Name: ix_sales_transactions_transaction_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_transaction_date ON public.sales_transactions USING btree (transaction_date);


--
-- Name: ix_sales_transactions_transaction_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_transaction_number ON public.sales_transactions USING btree (transaction_number);


--
-- Name: ix_sales_transactions_valid_until; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sales_transactions_valid_until ON public.sales_transactions USING btree (valid_until);


--
-- Name: quote_approvals quote_approvals_quote_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_approvals
    ADD CONSTRAINT quote_approvals_quote_id_fkey FOREIGN KEY (quote_id) REFERENCES public.sales_quotes(id) ON DELETE CASCADE;


--
-- Name: quote_versions quote_versions_quote_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quote_versions
    ADD CONSTRAINT quote_versions_quote_id_fkey FOREIGN KEY (quote_id) REFERENCES public.sales_quotes(id) ON DELETE CASCADE;


--
-- Name: sales_quote_line_items sales_quote_line_items_quote_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_quote_line_items
    ADD CONSTRAINT sales_quote_line_items_quote_id_fkey FOREIGN KEY (quote_id) REFERENCES public.sales_quotes(id) ON DELETE CASCADE;


--
-- Name: sales_transaction_line_items sales_transaction_line_items_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales_transaction_line_items
    ADD CONSTRAINT sales_transaction_line_items_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.sales_transactions(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict ScV57X0hlbucbTmOQ0WOvg1Fwlc88nFfReYvLAJIRj4LpeAXqGb5EVsv2Gxji57

