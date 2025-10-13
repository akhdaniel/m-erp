--
-- PostgreSQL database dump
--

\restrict 6uMPHAVzGYnvFsPXJZAOP5uUZweZdwmWxm5nKNu9mjChbSjp4fBboooJcs3Qfbr

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
-- Name: business_object_extensions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.business_object_extensions (
    id integer NOT NULL,
    entity_type character varying(100) NOT NULL,
    entity_id integer NOT NULL,
    field_name character varying(100) NOT NULL,
    field_type character varying(50) NOT NULL,
    field_value text,
    company_id integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    framework_version character varying(20)
);


ALTER TABLE public.business_object_extensions OWNER TO postgres;

--
-- Name: business_object_extensions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.business_object_extensions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.business_object_extensions_id_seq OWNER TO postgres;

--
-- Name: business_object_extensions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.business_object_extensions_id_seq OWNED BY public.business_object_extensions.id;


--
-- Name: business_object_field_definitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.business_object_field_definitions (
    id integer NOT NULL,
    entity_type character varying(100) NOT NULL,
    field_name character varying(100) NOT NULL,
    field_type character varying(50) NOT NULL,
    field_label character varying(200),
    field_description text,
    is_required boolean NOT NULL,
    default_value text,
    field_options text,
    display_order integer NOT NULL,
    company_id integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    framework_version character varying(20)
);


ALTER TABLE public.business_object_field_definitions OWNER TO postgres;

--
-- Name: business_object_field_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.business_object_field_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.business_object_field_definitions_id_seq OWNER TO postgres;

--
-- Name: business_object_field_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.business_object_field_definitions_id_seq OWNED BY public.business_object_field_definitions.id;


--
-- Name: business_object_validators; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.business_object_validators (
    id integer NOT NULL,
    entity_type character varying(100) NOT NULL,
    field_name character varying(100) NOT NULL,
    validator_type character varying(50) NOT NULL,
    validator_config text NOT NULL,
    validation_order integer NOT NULL,
    company_id integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    framework_version character varying(20)
);


ALTER TABLE public.business_object_validators OWNER TO postgres;

--
-- Name: business_object_validators_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.business_object_validators_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.business_object_validators_id_seq OWNER TO postgres;

--
-- Name: business_object_validators_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.business_object_validators_id_seq OWNED BY public.business_object_validators.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    legal_name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    email character varying(255),
    phone character varying(50),
    website character varying(255),
    tax_id character varying(100),
    street text,
    street2 text,
    city character varying(100),
    state character varying(100),
    zip character varying(20),
    country character varying(100),
    currency character varying(3),
    timezone character varying(50),
    logo_url text,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    framework_version character varying(20) DEFAULT '1.0.0'::character varying NOT NULL,
    CONSTRAINT companies_code_check CHECK ((length((code)::text) >= 2)),
    CONSTRAINT companies_name_check CHECK ((length((name)::text) >= 1))
);


ALTER TABLE public.companies OWNER TO postgres;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO postgres;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: company_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_users (
    id integer NOT NULL,
    company_id integer NOT NULL,
    user_id integer NOT NULL,
    role character varying(50) NOT NULL,
    is_default_company boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT company_users_role_check CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'manager'::character varying, 'user'::character varying, 'viewer'::character varying])::text[])))
);


ALTER TABLE public.company_users OWNER TO postgres;

--
-- Name: company_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_users_id_seq OWNER TO postgres;

--
-- Name: company_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_users_id_seq OWNED BY public.company_users.id;


--
-- Name: currencies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.currencies (
    id integer NOT NULL,
    code character varying(3) NOT NULL,
    name character varying(100) NOT NULL,
    symbol character varying(10) NOT NULL,
    decimal_places integer NOT NULL,
    rounding numeric(10,6) NOT NULL,
    "position" character varying(10) NOT NULL,
    thousands_sep character varying(1),
    decimal_sep character varying(1),
    is_active boolean NOT NULL,
    is_base boolean NOT NULL,
    company_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT currencies_code_length_check CHECK ((length((code)::text) = 3)),
    CONSTRAINT currencies_decimal_places_check CHECK ((decimal_places >= 0)),
    CONSTRAINT currencies_decimal_places_max_check CHECK ((decimal_places <= 6)),
    CONSTRAINT currencies_name_check CHECK ((length((name)::text) >= 1)),
    CONSTRAINT currencies_position_check CHECK ((("position")::text = ANY ((ARRAY['before'::character varying, 'after'::character varying])::text[]))),
    CONSTRAINT currencies_symbol_check CHECK ((length((symbol)::text) >= 1))
);


ALTER TABLE public.currencies OWNER TO postgres;

--
-- Name: currencies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.currencies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.currencies_id_seq OWNER TO postgres;

--
-- Name: currencies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.currencies_id_seq OWNED BY public.currencies.id;


--
-- Name: currency_rates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.currency_rates (
    id integer NOT NULL,
    currency_id integer NOT NULL,
    base_currency_id integer NOT NULL,
    rate numeric(20,10) NOT NULL,
    inverse_rate numeric(20,10) NOT NULL,
    date_start timestamp with time zone NOT NULL,
    date_end timestamp with time zone,
    source character varying(50),
    provider character varying(100),
    company_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT currency_rates_date_check CHECK (((date_end IS NULL) OR (date_end > date_start))),
    CONSTRAINT currency_rates_inverse_rate_positive_check CHECK ((inverse_rate > (0)::numeric)),
    CONSTRAINT currency_rates_rate_positive_check CHECK ((rate > (0)::numeric))
);


ALTER TABLE public.currency_rates OWNER TO postgres;

--
-- Name: currency_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.currency_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.currency_rates_id_seq OWNER TO postgres;

--
-- Name: currency_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.currency_rates_id_seq OWNED BY public.currency_rates.id;


--
-- Name: partner_addresses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partner_addresses (
    id integer NOT NULL,
    partner_id integer NOT NULL,
    address_type character varying(20) NOT NULL,
    street text NOT NULL,
    street2 text,
    city character varying(100) NOT NULL,
    state character varying(100),
    zip character varying(20),
    country character varying(100) NOT NULL,
    is_default boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT partner_addresses_type_check CHECK (((address_type)::text = ANY ((ARRAY['default'::character varying, 'billing'::character varying, 'shipping'::character varying, 'other'::character varying])::text[])))
);


ALTER TABLE public.partner_addresses OWNER TO postgres;

--
-- Name: partner_addresses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partner_addresses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partner_addresses_id_seq OWNER TO postgres;

--
-- Name: partner_addresses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partner_addresses_id_seq OWNED BY public.partner_addresses.id;


--
-- Name: partner_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partner_categories (
    id integer NOT NULL,
    company_id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    color character varying(7),
    parent_category_id integer,
    is_active boolean NOT NULL,
    is_default boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    framework_version character varying(50),
    CONSTRAINT partner_categories_code_check CHECK ((length((code)::text) >= 1)),
    CONSTRAINT partner_categories_color_check CHECK (((color IS NULL) OR ((color)::text ~ '^#[0-9A-Fa-f]{6}$'::text))),
    CONSTRAINT partner_categories_name_check CHECK ((length((name)::text) >= 1))
);


ALTER TABLE public.partner_categories OWNER TO postgres;

--
-- Name: partner_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partner_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partner_categories_id_seq OWNER TO postgres;

--
-- Name: partner_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partner_categories_id_seq OWNED BY public.partner_categories.id;


--
-- Name: partner_communications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partner_communications (
    id integer NOT NULL,
    partner_id integer NOT NULL,
    partner_contact_id integer,
    communication_type character varying(50) NOT NULL,
    subject character varying(500) NOT NULL,
    content text,
    direction character varying(20) NOT NULL,
    initiated_by character varying(255),
    participants text,
    scheduled_at timestamp without time zone,
    completed_at timestamp without time zone,
    status character varying(20) NOT NULL,
    priority character varying(20) NOT NULL,
    outcome character varying(100),
    follow_up_required boolean NOT NULL,
    follow_up_date timestamp without time zone,
    tags text,
    attachments_count integer NOT NULL,
    external_reference character varying(255),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT partner_communications_direction_check CHECK (((direction)::text = ANY ((ARRAY['inbound'::character varying, 'outbound'::character varying])::text[]))),
    CONSTRAINT partner_communications_priority_check CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'normal'::character varying, 'high'::character varying, 'urgent'::character varying])::text[]))),
    CONSTRAINT partner_communications_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'cancelled'::character varying, 'failed'::character varying])::text[]))),
    CONSTRAINT partner_communications_subject_check CHECK ((length((subject)::text) >= 1)),
    CONSTRAINT partner_communications_type_check CHECK (((communication_type)::text = ANY ((ARRAY['email'::character varying, 'phone'::character varying, 'meeting'::character varying, 'video_call'::character varying, 'letter'::character varying, 'fax'::character varying, 'text'::character varying, 'other'::character varying])::text[])))
);


ALTER TABLE public.partner_communications OWNER TO postgres;

--
-- Name: partner_communications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partner_communications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partner_communications_id_seq OWNER TO postgres;

--
-- Name: partner_communications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partner_communications_id_seq OWNED BY public.partner_communications.id;


--
-- Name: partner_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partner_contacts (
    id integer NOT NULL,
    partner_id integer NOT NULL,
    name character varying(255) NOT NULL,
    title character varying(100),
    email character varying(255),
    phone character varying(50),
    mobile character varying(50),
    is_primary boolean NOT NULL,
    department character varying(100),
    notes text,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT partner_contacts_name_check CHECK ((length((name)::text) >= 1))
);


ALTER TABLE public.partner_contacts OWNER TO postgres;

--
-- Name: partner_contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partner_contacts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partner_contacts_id_seq OWNER TO postgres;

--
-- Name: partner_contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partner_contacts_id_seq OWNED BY public.partner_contacts.id;


--
-- Name: partners; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partners (
    id integer NOT NULL,
    company_id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(50),
    partner_type character varying(20) NOT NULL,
    email character varying(255),
    phone character varying(50),
    mobile character varying(50),
    website character varying(255),
    tax_id character varying(100),
    industry character varying(100),
    parent_partner_id integer,
    is_company boolean NOT NULL,
    is_customer boolean NOT NULL,
    is_supplier boolean NOT NULL,
    is_vendor boolean NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    framework_version character varying(20) DEFAULT '1.0.0'::character varying NOT NULL,
    category_id integer,
    CONSTRAINT partners_name_check CHECK ((length((name)::text) >= 1)),
    CONSTRAINT partners_type_check CHECK (((partner_type)::text = ANY ((ARRAY['customer'::character varying, 'supplier'::character varying, 'vendor'::character varying, 'both'::character varying])::text[])))
);


ALTER TABLE public.partners OWNER TO postgres;

--
-- Name: partners_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partners_id_seq OWNER TO postgres;

--
-- Name: partners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partners_id_seq OWNED BY public.partners.id;


--
-- Name: business_object_extensions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_extensions ALTER COLUMN id SET DEFAULT nextval('public.business_object_extensions_id_seq'::regclass);


--
-- Name: business_object_field_definitions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_field_definitions ALTER COLUMN id SET DEFAULT nextval('public.business_object_field_definitions_id_seq'::regclass);


--
-- Name: business_object_validators id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_validators ALTER COLUMN id SET DEFAULT nextval('public.business_object_validators_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: company_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_users ALTER COLUMN id SET DEFAULT nextval('public.company_users_id_seq'::regclass);


--
-- Name: currencies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currencies ALTER COLUMN id SET DEFAULT nextval('public.currencies_id_seq'::regclass);


--
-- Name: currency_rates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currency_rates ALTER COLUMN id SET DEFAULT nextval('public.currency_rates_id_seq'::regclass);


--
-- Name: partner_addresses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_addresses ALTER COLUMN id SET DEFAULT nextval('public.partner_addresses_id_seq'::regclass);


--
-- Name: partner_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_categories ALTER COLUMN id SET DEFAULT nextval('public.partner_categories_id_seq'::regclass);


--
-- Name: partner_communications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_communications ALTER COLUMN id SET DEFAULT nextval('public.partner_communications_id_seq'::regclass);


--
-- Name: partner_contacts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_contacts ALTER COLUMN id SET DEFAULT nextval('public.partner_contacts_id_seq'::regclass);


--
-- Name: partners id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners ALTER COLUMN id SET DEFAULT nextval('public.partners_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
20250804_102000
\.


--
-- Data for Name: business_object_extensions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.business_object_extensions (id, entity_type, entity_id, field_name, field_type, field_value, company_id, is_active, created_at, updated_at, framework_version) FROM stdin;
\.


--
-- Data for Name: business_object_field_definitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.business_object_field_definitions (id, entity_type, field_name, field_type, field_label, field_description, is_required, default_value, field_options, display_order, company_id, is_active, created_at, updated_at, framework_version) FROM stdin;
\.


--
-- Data for Name: business_object_validators; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.business_object_validators (id, entity_type, field_name, validator_type, validator_config, validation_order, company_id, is_active, created_at, updated_at, framework_version) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (id, name, legal_name, code, email, phone, website, tax_id, street, street2, city, state, zip, country, currency, timezone, logo_url, is_active, created_at, updated_at, framework_version) FROM stdin;
1	Supplier XY	Company 1	006	d@dkc.com	\N	\N	\N	ghgh	\N	\N	\N	\N	\N	USD	UTC	\N	t	2025-08-24 10:01:48.917463	2025-08-24 10:01:48.917471	1.0.0
\.


--
-- Data for Name: company_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_users (id, company_id, user_id, role, is_default_company, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: currencies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.currencies (id, code, name, symbol, decimal_places, rounding, "position", thousands_sep, decimal_sep, is_active, is_base, company_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: currency_rates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.currency_rates (id, currency_id, base_currency_id, rate, inverse_rate, date_start, date_end, source, provider, company_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partner_addresses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partner_addresses (id, partner_id, address_type, street, street2, city, state, zip, country, is_default, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partner_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partner_categories (id, company_id, name, code, description, color, parent_category_id, is_active, is_default, created_at, updated_at, framework_version) FROM stdin;
\.


--
-- Data for Name: partner_communications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partner_communications (id, partner_id, partner_contact_id, communication_type, subject, content, direction, initiated_by, participants, scheduled_at, completed_at, status, priority, outcome, follow_up_required, follow_up_date, tags, attachments_count, external_reference, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partner_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partner_contacts (id, partner_id, name, title, email, phone, mobile, is_primary, department, notes, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: partners; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partners (id, company_id, name, code, partner_type, email, phone, mobile, website, tax_id, industry, parent_partner_id, is_company, is_customer, is_supplier, is_vendor, is_active, created_at, updated_at, framework_version, category_id) FROM stdin;
2	1	Cusotmer Name	\N	customer	emsi@hjdasf.com	\N	\N	\N	\N	\N	\N	f	t	f	f	t	2025-09-19 06:06:00.257666	2025-09-19 06:06:00.257674	1.0.0	\N
3	1	Customer 3	\N	customer	aaadd@kdslfks.com	\N	\N	\N	\N	\N	\N	f	t	f	f	t	2025-09-19 06:27:08.51299	2025-09-19 06:31:18.579647	1.0.0	\N
1	1	Customer1	\N	customer	rr@dd.com	\N	\N	\N	\N	\N	\N	f	t	f	f	t	2025-09-19 06:01:35.215785	2025-09-30 08:13:14.250782	1.0.0	\N
\.


--
-- Name: business_object_extensions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.business_object_extensions_id_seq', 1, false);


--
-- Name: business_object_field_definitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.business_object_field_definitions_id_seq', 1, false);


--
-- Name: business_object_validators_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.business_object_validators_id_seq', 1, false);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.companies_id_seq', 1, true);


--
-- Name: company_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.company_users_id_seq', 1, false);


--
-- Name: currencies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.currencies_id_seq', 1, false);


--
-- Name: currency_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.currency_rates_id_seq', 1, false);


--
-- Name: partner_addresses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partner_addresses_id_seq', 1, false);


--
-- Name: partner_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partner_categories_id_seq', 1, false);


--
-- Name: partner_communications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partner_communications_id_seq', 1, false);


--
-- Name: partner_contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partner_contacts_id_seq', 1, false);


--
-- Name: partners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partners_id_seq', 3, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: business_object_extensions business_object_extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_extensions
    ADD CONSTRAINT business_object_extensions_pkey PRIMARY KEY (id);


--
-- Name: business_object_field_definitions business_object_field_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_field_definitions
    ADD CONSTRAINT business_object_field_definitions_pkey PRIMARY KEY (id);


--
-- Name: business_object_validators business_object_validators_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_validators
    ADD CONSTRAINT business_object_validators_pkey PRIMARY KEY (id);


--
-- Name: companies companies_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_code_key UNIQUE (code);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: company_users company_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_users
    ADD CONSTRAINT company_users_pkey PRIMARY KEY (id);


--
-- Name: company_users company_users_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_users
    ADD CONSTRAINT company_users_unique UNIQUE (company_id, user_id);


--
-- Name: currencies currencies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currencies
    ADD CONSTRAINT currencies_pkey PRIMARY KEY (id);


--
-- Name: currency_rates currency_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currency_rates
    ADD CONSTRAINT currency_rates_pkey PRIMARY KEY (id);


--
-- Name: partner_addresses partner_addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_addresses
    ADD CONSTRAINT partner_addresses_pkey PRIMARY KEY (id);


--
-- Name: partner_categories partner_categories_company_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_categories
    ADD CONSTRAINT partner_categories_company_code_unique UNIQUE (company_id, code);


--
-- Name: partner_categories partner_categories_company_name_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_categories
    ADD CONSTRAINT partner_categories_company_name_unique UNIQUE (company_id, name);


--
-- Name: partner_categories partner_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_categories
    ADD CONSTRAINT partner_categories_pkey PRIMARY KEY (id);


--
-- Name: partner_communications partner_communications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_communications
    ADD CONSTRAINT partner_communications_pkey PRIMARY KEY (id);


--
-- Name: partner_contacts partner_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_contacts
    ADD CONSTRAINT partner_contacts_pkey PRIMARY KEY (id);


--
-- Name: partners partners_company_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_company_code_unique UNIQUE (company_id, code);


--
-- Name: partners partners_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_pkey PRIMARY KEY (id);


--
-- Name: business_object_extensions uq_extensions_entity_field_company; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_extensions
    ADD CONSTRAINT uq_extensions_entity_field_company UNIQUE (entity_type, entity_id, field_name, company_id);


--
-- Name: business_object_field_definitions uq_field_definitions_entity_field_company; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_field_definitions
    ADD CONSTRAINT uq_field_definitions_entity_field_company UNIQUE (entity_type, field_name, company_id);


--
-- Name: idx_currencies_active_base; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_currencies_active_base ON public.currencies USING btree (is_active, is_base);


--
-- Name: idx_currencies_company_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_currencies_company_code ON public.currencies USING btree (company_id, code);


--
-- Name: idx_currency_rates_current; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_currency_rates_current ON public.currency_rates USING btree (currency_id, base_currency_id, company_id, date_end);


--
-- Name: idx_currency_rates_lookup; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_currency_rates_lookup ON public.currency_rates USING btree (currency_id, base_currency_id, company_id, date_start);


--
-- Name: idx_extensions_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_extensions_active ON public.business_object_extensions USING btree (is_active);


--
-- Name: idx_extensions_entity_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_extensions_entity_company ON public.business_object_extensions USING btree (entity_type, entity_id, company_id);


--
-- Name: idx_extensions_field_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_extensions_field_type ON public.business_object_extensions USING btree (field_type);


--
-- Name: idx_field_definitions_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_field_definitions_active ON public.business_object_field_definitions USING btree (is_active);


--
-- Name: idx_field_definitions_entity_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_field_definitions_entity_company ON public.business_object_field_definitions USING btree (entity_type, company_id);


--
-- Name: idx_field_definitions_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_field_definitions_order ON public.business_object_field_definitions USING btree (display_order);


--
-- Name: idx_partners_industry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_partners_industry ON public.partners USING btree (industry, company_id);


--
-- Name: idx_validators_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validators_company ON public.business_object_validators USING btree (company_id);


--
-- Name: idx_validators_entity_field; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validators_entity_field ON public.business_object_validators USING btree (entity_type, field_name);


--
-- Name: idx_validators_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validators_order ON public.business_object_validators USING btree (validation_order);


--
-- Name: idx_validators_type_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validators_type_active ON public.business_object_validators USING btree (validator_type, is_active);


--
-- Name: ix_business_object_extensions_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_extensions_company_id ON public.business_object_extensions USING btree (company_id);


--
-- Name: ix_business_object_extensions_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_extensions_entity_id ON public.business_object_extensions USING btree (entity_id);


--
-- Name: ix_business_object_extensions_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_extensions_entity_type ON public.business_object_extensions USING btree (entity_type);


--
-- Name: ix_business_object_extensions_field_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_extensions_field_name ON public.business_object_extensions USING btree (field_name);


--
-- Name: ix_business_object_extensions_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_extensions_is_active ON public.business_object_extensions USING btree (is_active);


--
-- Name: ix_business_object_field_definitions_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_field_definitions_company_id ON public.business_object_field_definitions USING btree (company_id);


--
-- Name: ix_business_object_field_definitions_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_field_definitions_entity_type ON public.business_object_field_definitions USING btree (entity_type);


--
-- Name: ix_business_object_field_definitions_field_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_field_definitions_field_name ON public.business_object_field_definitions USING btree (field_name);


--
-- Name: ix_business_object_field_definitions_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_field_definitions_is_active ON public.business_object_field_definitions USING btree (is_active);


--
-- Name: ix_business_object_validators_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_validators_company_id ON public.business_object_validators USING btree (company_id);


--
-- Name: ix_business_object_validators_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_validators_entity_type ON public.business_object_validators USING btree (entity_type);


--
-- Name: ix_business_object_validators_field_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_validators_field_name ON public.business_object_validators USING btree (field_name);


--
-- Name: ix_business_object_validators_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_validators_is_active ON public.business_object_validators USING btree (is_active);


--
-- Name: ix_business_object_validators_validator_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_business_object_validators_validator_type ON public.business_object_validators USING btree (validator_type);


--
-- Name: ix_companies_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_companies_code ON public.companies USING btree (code);


--
-- Name: ix_companies_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_companies_is_active ON public.companies USING btree (is_active);


--
-- Name: ix_company_users_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_company_users_company_id ON public.company_users USING btree (company_id);


--
-- Name: ix_company_users_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_company_users_user_id ON public.company_users USING btree (user_id);


--
-- Name: ix_currencies_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currencies_code ON public.currencies USING btree (code);


--
-- Name: ix_currencies_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currencies_is_active ON public.currencies USING btree (is_active);


--
-- Name: ix_currencies_is_base; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currencies_is_base ON public.currencies USING btree (is_base);


--
-- Name: ix_currency_rates_base_currency_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currency_rates_base_currency_id ON public.currency_rates USING btree (base_currency_id);


--
-- Name: ix_currency_rates_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currency_rates_company_id ON public.currency_rates USING btree (company_id);


--
-- Name: ix_currency_rates_currency_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currency_rates_currency_id ON public.currency_rates USING btree (currency_id);


--
-- Name: ix_currency_rates_date_end; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currency_rates_date_end ON public.currency_rates USING btree (date_end);


--
-- Name: ix_currency_rates_date_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_currency_rates_date_start ON public.currency_rates USING btree (date_start);


--
-- Name: ix_partner_addresses_address_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_addresses_address_type ON public.partner_addresses USING btree (address_type);


--
-- Name: ix_partner_addresses_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_addresses_partner_id ON public.partner_addresses USING btree (partner_id);


--
-- Name: ix_partner_categories_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_categories_company_id ON public.partner_categories USING btree (company_id);


--
-- Name: ix_partner_categories_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_categories_is_active ON public.partner_categories USING btree (is_active);


--
-- Name: ix_partner_categories_parent_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_categories_parent_category_id ON public.partner_categories USING btree (parent_category_id);


--
-- Name: ix_partner_communications_communication_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_communication_type ON public.partner_communications USING btree (communication_type);


--
-- Name: ix_partner_communications_completed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_completed_at ON public.partner_communications USING btree (completed_at);


--
-- Name: ix_partner_communications_direction; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_direction ON public.partner_communications USING btree (direction);


--
-- Name: ix_partner_communications_follow_up_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_follow_up_date ON public.partner_communications USING btree (follow_up_date);


--
-- Name: ix_partner_communications_partner_contact_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_partner_contact_id ON public.partner_communications USING btree (partner_contact_id);


--
-- Name: ix_partner_communications_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_partner_id ON public.partner_communications USING btree (partner_id);


--
-- Name: ix_partner_communications_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_priority ON public.partner_communications USING btree (priority);


--
-- Name: ix_partner_communications_scheduled_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_scheduled_at ON public.partner_communications USING btree (scheduled_at);


--
-- Name: ix_partner_communications_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_communications_status ON public.partner_communications USING btree (status);


--
-- Name: ix_partner_contacts_is_primary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_contacts_is_primary ON public.partner_contacts USING btree (is_primary);


--
-- Name: ix_partner_contacts_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partner_contacts_partner_id ON public.partner_contacts USING btree (partner_id);


--
-- Name: ix_partners_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_category_id ON public.partners USING btree (category_id);


--
-- Name: ix_partners_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_company_id ON public.partners USING btree (company_id);


--
-- Name: ix_partners_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_is_active ON public.partners USING btree (is_active);


--
-- Name: ix_partners_parent_partner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_parent_partner_id ON public.partners USING btree (parent_partner_id);


--
-- Name: ix_partners_partner_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_partners_partner_type ON public.partners USING btree (partner_type);


--
-- Name: business_object_extensions business_object_extensions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_extensions
    ADD CONSTRAINT business_object_extensions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: business_object_field_definitions business_object_field_definitions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_field_definitions
    ADD CONSTRAINT business_object_field_definitions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: business_object_validators business_object_validators_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_object_validators
    ADD CONSTRAINT business_object_validators_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: company_users company_users_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_users
    ADD CONSTRAINT company_users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: partners fk_partners_category_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT fk_partners_category_id FOREIGN KEY (category_id) REFERENCES public.partner_categories(id) ON DELETE SET NULL;


--
-- Name: partner_addresses partner_addresses_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_addresses
    ADD CONSTRAINT partner_addresses_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE;


--
-- Name: partner_categories partner_categories_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_categories
    ADD CONSTRAINT partner_categories_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: partner_categories partner_categories_parent_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_categories
    ADD CONSTRAINT partner_categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES public.partner_categories(id) ON DELETE SET NULL;


--
-- Name: partner_communications partner_communications_partner_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_communications
    ADD CONSTRAINT partner_communications_partner_contact_id_fkey FOREIGN KEY (partner_contact_id) REFERENCES public.partner_contacts(id) ON DELETE SET NULL;


--
-- Name: partner_communications partner_communications_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_communications
    ADD CONSTRAINT partner_communications_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE;


--
-- Name: partner_contacts partner_contacts_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partner_contacts
    ADD CONSTRAINT partner_contacts_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE;


--
-- Name: partners partners_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: partners partners_parent_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_parent_partner_id_fkey FOREIGN KEY (parent_partner_id) REFERENCES public.partners(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict 6uMPHAVzGYnvFsPXJZAOP5uUZweZdwmWxm5nKNu9mjChbSjp4fBboooJcs3Qfbr

