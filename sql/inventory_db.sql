--
-- PostgreSQL database dump
--

\restrict D0tupRLU5OFHJ8OmgxvqmhT940Wd5d7bmafC63zlFaNr1C4KgEdUROYKTOO16aA

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
-- Name: locationtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.locationtype AS ENUM (
    'ZONE',
    'AISLE',
    'RACK',
    'SHELF',
    'BIN',
    'FLOOR',
    'DOCK',
    'STAGING',
    'QUALITY',
    'DAMAGED'
);


ALTER TYPE public.locationtype OWNER TO postgres;

--
-- Name: productstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.productstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'DISCONTINUED',
    'DRAFT'
);


ALTER TYPE public.productstatus OWNER TO postgres;

--
-- Name: producttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.producttype AS ENUM (
    'PHYSICAL',
    'DIGITAL',
    'SERVICE',
    'KIT'
);


ALTER TYPE public.producttype OWNER TO postgres;

--
-- Name: receivinglinestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.receivinglinestatus AS ENUM (
    'PENDING',
    'PARTIAL',
    'COMPLETE',
    'OVER_RECEIVED',
    'DAMAGED',
    'REJECTED'
);


ALTER TYPE public.receivinglinestatus OWNER TO postgres;

--
-- Name: receivingstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.receivingstatus AS ENUM (
    'PENDING',
    'PARTIAL',
    'COMPLETE',
    'CANCELLED',
    'ON_HOLD'
);


ALTER TYPE public.receivingstatus OWNER TO postgres;

--
-- Name: stockmovementtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.stockmovementtype AS ENUM (
    'RECEIPT',
    'ADJUSTMENT_IN',
    'TRANSFER_IN',
    'RETURN_IN',
    'PRODUCTION_IN',
    'SALE',
    'ADJUSTMENT_OUT',
    'TRANSFER_OUT',
    'RETURN_OUT',
    'WASTE',
    'PRODUCTION_OUT',
    'CYCLE_COUNT',
    'RESERVATION',
    'RELEASE_RESERVATION'
);


ALTER TYPE public.stockmovementtype OWNER TO postgres;

--
-- Name: unitofmeasure; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.unitofmeasure AS ENUM (
    'EACH',
    'DOZEN',
    'CASE',
    'KILOGRAM',
    'GRAM',
    'POUND',
    'OUNCE',
    'LITER',
    'MILLILITER',
    'METER',
    'CENTIMETER',
    'INCH',
    'FOOT',
    'SQUARE_METER',
    'SQUARE_FOOT',
    'CUBIC_METER',
    'CUBIC_FOOT'
);


ALTER TYPE public.unitofmeasure OWNER TO postgres;

--
-- Name: warehousetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.warehousetype AS ENUM (
    'MAIN',
    'DISTRIBUTION',
    'RETAIL',
    'MANUFACTURING',
    'TRANSIT',
    'THIRD_PARTY',
    'VIRTUAL'
);


ALTER TYPE public.warehousetype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: product_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_categories (
    name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    parent_category_id integer,
    display_order integer NOT NULL,
    color character varying(7),
    icon character varying(100),
    slug character varying(255),
    meta_title character varying(255),
    meta_description text,
    is_active boolean NOT NULL,
    product_count integer NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.product_categories OWNER TO postgres;

--
-- Name: product_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_categories_id_seq OWNER TO postgres;

--
-- Name: product_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_categories_id_seq OWNED BY public.product_categories.id;


--
-- Name: product_variants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_variants (
    parent_product_id integer NOT NULL,
    variant_name character varying(255) NOT NULL,
    sku character varying(100) NOT NULL,
    barcode character varying(100),
    attributes json,
    list_price numeric(15,2),
    cost_price numeric(15,2),
    price_adjustment numeric(15,2),
    minimum_stock_level numeric(10,2),
    maximum_stock_level numeric(10,2),
    reorder_point numeric(10,2),
    reorder_quantity numeric(10,2),
    weight numeric(10,4),
    dimensions json,
    images json,
    primary_image character varying(500),
    is_active boolean NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.product_variants OWNER TO postgres;

--
-- Name: product_variants_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_variants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_variants_id_seq OWNER TO postgres;

--
-- Name: product_variants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_variants_id_seq OWNED BY public.product_variants.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    name character varying(255) NOT NULL,
    description text,
    short_description character varying(500),
    sku character varying(100) NOT NULL,
    barcode character varying(100),
    manufacturer_part_number character varying(100),
    category_id integer,
    product_type public.producttype NOT NULL,
    status public.productstatus NOT NULL,
    list_price numeric(15,2),
    cost_price numeric(15,2),
    currency_code character varying(3) NOT NULL,
    unit_of_measure public.unitofmeasure NOT NULL,
    weight numeric(10,4),
    weight_unit character varying(10),
    dimensions json,
    track_inventory boolean NOT NULL,
    minimum_stock_level numeric(10,2),
    maximum_stock_level numeric(10,2),
    reorder_point numeric(10,2),
    reorder_quantity numeric(10,2),
    lead_time_days integer,
    primary_supplier_id integer,
    supplier_product_code character varying(100),
    quality_control_required boolean NOT NULL,
    hazardous_material boolean NOT NULL,
    expiration_tracking boolean NOT NULL,
    batch_tracking boolean NOT NULL,
    serial_tracking boolean NOT NULL,
    web_enabled boolean NOT NULL,
    meta_title character varying(255),
    meta_description text,
    tags json,
    images json,
    primary_image character varying(500),
    documents json,
    custom_attributes json,
    is_active boolean NOT NULL,
    discontinued_date timestamp without time zone,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: receiving_line_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.receiving_line_items (
    receiving_record_id integer NOT NULL,
    product_id integer NOT NULL,
    product_variant_id integer,
    line_number integer NOT NULL,
    quantity_expected numeric(15,4) NOT NULL,
    quantity_received numeric(15,4) NOT NULL,
    quantity_accepted numeric(15,4) NOT NULL,
    quantity_rejected numeric(15,4) NOT NULL,
    quantity_damaged numeric(15,4) NOT NULL,
    unit_cost numeric(15,4),
    total_cost numeric(15,2),
    batch_number character varying(100),
    serial_numbers json,
    expiration_date timestamp without time zone,
    put_away_location_id integer,
    status public.receivinglinestatus NOT NULL,
    received_date timestamp without time zone,
    quality_check_required boolean NOT NULL,
    quality_check_passed boolean,
    quality_notes text,
    inspected_by_user_id integer,
    inspected_at timestamp without time zone,
    rejection_reason text,
    damage_description text,
    notes text,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.receiving_line_items OWNER TO postgres;

--
-- Name: receiving_line_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.receiving_line_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.receiving_line_items_id_seq OWNER TO postgres;

--
-- Name: receiving_line_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.receiving_line_items_id_seq OWNED BY public.receiving_line_items.id;


--
-- Name: receiving_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.receiving_records (
    receipt_number character varying(100) NOT NULL,
    source_document_type character varying(50) NOT NULL,
    source_document_id integer NOT NULL,
    source_document_number character varying(100),
    supplier_id integer NOT NULL,
    supplier_invoice_number character varying(100),
    supplier_delivery_note character varying(100),
    warehouse_id integer NOT NULL,
    receiving_location_id integer,
    expected_date timestamp without time zone,
    received_date timestamp without time zone,
    scheduled_date timestamp without time zone,
    status public.receivingstatus NOT NULL,
    total_quantity_expected numeric(15,4) NOT NULL,
    total_quantity_received numeric(15,4) NOT NULL,
    total_value_expected numeric(15,2),
    total_value_received numeric(15,2),
    quality_inspection_required boolean NOT NULL,
    quality_inspection_passed boolean,
    quality_notes text,
    received_by_user_id integer,
    approved_by_user_id integer,
    approved_at timestamp without time zone,
    carrier_name character varying(255),
    tracking_number character varying(100),
    freight_cost numeric(10,2),
    notes text,
    attachments json,
    is_active boolean NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.receiving_records OWNER TO postgres;

--
-- Name: receiving_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.receiving_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.receiving_records_id_seq OWNER TO postgres;

--
-- Name: receiving_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.receiving_records_id_seq OWNED BY public.receiving_records.id;


--
-- Name: stock_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_levels (
    product_id integer NOT NULL,
    product_variant_id integer,
    warehouse_location_id integer NOT NULL,
    quantity_on_hand numeric(15,4) NOT NULL,
    quantity_reserved numeric(15,4) NOT NULL,
    quantity_available numeric(15,4) NOT NULL,
    quantity_incoming numeric(15,4) NOT NULL,
    batch_number character varying(100),
    serial_numbers json,
    expiration_date timestamp without time zone,
    unit_cost numeric(15,4),
    total_cost numeric(15,2),
    cost_method character varying(20),
    last_movement_date timestamp without time zone,
    last_movement_type public.stockmovementtype,
    last_count_date timestamp without time zone,
    is_active boolean NOT NULL,
    negative_stock_allowed boolean NOT NULL,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.stock_levels OWNER TO postgres;

--
-- Name: stock_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_levels_id_seq OWNER TO postgres;

--
-- Name: stock_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_levels_id_seq OWNED BY public.stock_levels.id;


--
-- Name: stock_movements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_movements (
    product_id integer NOT NULL,
    product_variant_id integer,
    warehouse_location_id integer NOT NULL,
    from_location_id integer,
    to_location_id integer,
    movement_type public.stockmovementtype NOT NULL,
    movement_date timestamp without time zone NOT NULL,
    quantity numeric(15,4) NOT NULL,
    unit_cost numeric(15,4),
    total_cost numeric(15,2),
    batch_number character varying(100),
    serial_numbers json,
    expiration_date timestamp without time zone,
    source_document_type character varying(50),
    source_document_id integer,
    source_document_number character varying(100),
    created_by_user_id integer NOT NULL,
    approved_by_user_id integer,
    approved_at timestamp without time zone,
    reference_number character varying(100),
    notes text,
    reason_code character varying(50),
    quality_check_required boolean NOT NULL,
    quality_check_passed boolean,
    quality_notes text,
    inspected_by_user_id integer,
    inspected_at timestamp without time zone,
    quantity_before numeric(15,4),
    quantity_after numeric(15,4),
    is_reversed boolean NOT NULL,
    reversed_by_movement_id integer,
    reversed_at timestamp without time zone,
    movement_metadata json,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.stock_movements OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_movements_id_seq OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_movements_id_seq OWNED BY public.stock_movements.id;


--
-- Name: warehouse_locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_locations (
    warehouse_id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(100) NOT NULL,
    barcode character varying(100),
    parent_location_id integer,
    location_type public.locationtype NOT NULL,
    level integer NOT NULL,
    position_x numeric(8,2),
    position_y numeric(8,2),
    position_z numeric(6,2),
    max_weight_kg numeric(10,2),
    max_volume_cbm numeric(10,4),
    max_items integer,
    current_weight_kg numeric(10,2),
    current_volume_cbm numeric(10,4),
    current_items integer,
    allow_mixed_products boolean NOT NULL,
    allow_mixed_batches boolean NOT NULL,
    require_picking_confirmation boolean NOT NULL,
    climate_controlled boolean NOT NULL,
    temperature_min numeric(5,2),
    temperature_max numeric(5,2),
    humidity_min numeric(5,2),
    humidity_max numeric(5,2),
    pick_sequence integer,
    putaway_sequence integer,
    abc_classification character varying(1),
    restricted_access boolean NOT NULL,
    access_permissions json,
    hazmat_approved boolean NOT NULL,
    last_inspected_date timestamp without time zone,
    next_inspection_date timestamp without time zone,
    inspection_frequency_days integer,
    is_active boolean NOT NULL,
    is_blocked boolean NOT NULL,
    blocked_reason character varying(255),
    blocked_until timestamp without time zone,
    notes text,
    custom_attributes json,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.warehouse_locations OWNER TO postgres;

--
-- Name: warehouse_locations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouse_locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouse_locations_id_seq OWNER TO postgres;

--
-- Name: warehouse_locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouse_locations_id_seq OWNED BY public.warehouse_locations.id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouses (
    name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    warehouse_type public.warehousetype NOT NULL,
    address_line_1 character varying(255),
    address_line_2 character varying(255),
    city character varying(100),
    state_province character varying(100),
    postal_code character varying(20),
    country_code character varying(3),
    phone character varying(50),
    email character varying(255),
    contact_person character varying(255),
    latitude numeric(10,8),
    longitude numeric(11,8),
    timezone character varying(50),
    operating_hours json,
    currency_code character varying(3),
    capabilities json,
    total_area_sqm numeric(12,2),
    storage_area_sqm numeric(12,2),
    ceiling_height_m numeric(6,2),
    dock_doors_count integer,
    default_cost_center character varying(50),
    labor_cost_per_hour numeric(8,2),
    storage_cost_per_sqm numeric(8,4),
    allow_negative_stock boolean NOT NULL,
    require_location_tracking boolean NOT NULL,
    enable_cycle_counting boolean NOT NULL,
    default_receiving_location_id integer,
    default_shipping_location_id integer,
    is_active boolean NOT NULL,
    is_primary boolean NOT NULL,
    warehouse_manager_user_id integer,
    last_cycle_count_date timestamp without time zone,
    company_id integer NOT NULL,
    framework_version character varying(50),
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.warehouses OWNER TO postgres;

--
-- Name: warehouses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouses_id_seq OWNER TO postgres;

--
-- Name: warehouses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouses_id_seq OWNED BY public.warehouses.id;


--
-- Name: product_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories ALTER COLUMN id SET DEFAULT nextval('public.product_categories_id_seq'::regclass);


--
-- Name: product_variants id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_variants ALTER COLUMN id SET DEFAULT nextval('public.product_variants_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: receiving_line_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_line_items ALTER COLUMN id SET DEFAULT nextval('public.receiving_line_items_id_seq'::regclass);


--
-- Name: receiving_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_records ALTER COLUMN id SET DEFAULT nextval('public.receiving_records_id_seq'::regclass);


--
-- Name: stock_levels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels ALTER COLUMN id SET DEFAULT nextval('public.stock_levels_id_seq'::regclass);


--
-- Name: stock_movements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements ALTER COLUMN id SET DEFAULT nextval('public.stock_movements_id_seq'::regclass);


--
-- Name: warehouse_locations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations ALTER COLUMN id SET DEFAULT nextval('public.warehouse_locations_id_seq'::regclass);


--
-- Name: warehouses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses ALTER COLUMN id SET DEFAULT nextval('public.warehouses_id_seq'::regclass);


--
-- Data for Name: product_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_categories (name, code, description, parent_category_id, display_order, color, icon, slug, meta_title, meta_description, is_active, product_count, company_id, framework_version, id, created_at, updated_at) FROM stdin;
Electronics & Gadgets	ELECTRONICS	Electronic products, devices, and gadgets	\N	0	\N	\N	\N	\N	\N	f	0	1	1.0.0	1	2025-09-02 14:19:16.081435	2025-09-02 14:20:46.509481
Electronics	ELEC001	\N	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	2	2025-09-02 14:21:52.103887	2025-09-02 14:21:52.103894
Mobile Phones	MOB001	\N	2	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	4	2025-09-02 14:22:30.317545	2025-09-02 14:22:30.317557
Test Category	TEST001	\N	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	5	2025-09-02 22:44:42.604885	2025-09-02 22:44:42.604898
Test Category 2	TEST002	\N	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	6	2025-09-02 22:46:29.264073	2025-09-02 22:46:29.26408
Test Valid Category	TESTVALID	A valid test category	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	7	2025-09-02 22:48:08.87031	2025-09-02 22:48:08.870318
Makanan Kering	23045	\N	\N	0	\N	food	\N	\N	\N	t	0	1	1.0.0	8	2025-09-02 23:09:24.723922	2025-09-02 23:09:47.428474
Cteg0	C1212	\N	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	9	2025-09-03 04:33:46.457733	2025-09-03 04:33:46.457738
Computers	COMP001	\N	2	0	\N	\N	\N	\N	\N	t	1	1	1.0.0	3	2025-09-02 14:22:30.272012	2025-09-03 05:47:26.693209
543263	436	\N	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	10	2025-09-03 05:53:58.603145	2025-09-03 05:53:58.603151
123423	2222	\N	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	11	2025-09-03 05:54:10.032743	2025-09-03 05:54:10.032754
11111	1111	\N	11	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	12	2025-09-03 05:54:26.645307	2025-09-03 05:54:26.645318
Cate999	999	\N	\N	0	\N	\N	\N	\N	\N	t	0	1	1.0.0	13	2025-09-04 23:30:31.824566	2025-09-04 23:30:31.824574
\.


--
-- Data for Name: product_variants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_variants (parent_product_id, variant_name, sku, barcode, attributes, list_price, cost_price, price_adjustment, minimum_stock_level, maximum_stock_level, reorder_point, reorder_quantity, weight, dimensions, images, primary_image, is_active, company_id, framework_version, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (name, description, short_description, sku, barcode, manufacturer_part_number, category_id, product_type, status, list_price, cost_price, currency_code, unit_of_measure, weight, weight_unit, dimensions, track_inventory, minimum_stock_level, maximum_stock_level, reorder_point, reorder_quantity, lead_time_days, primary_supplier_id, supplier_product_code, quality_control_required, hazardous_material, expiration_tracking, batch_tracking, serial_tracking, web_enabled, meta_title, meta_description, tags, images, primary_image, documents, custom_attributes, is_active, discontinued_date, company_id, framework_version, id, created_at, updated_at) FROM stdin;
produk name	\N	\N	produk sku 001	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	1	2025-09-01 06:16:19.42942	2025-09-01 06:16:19.429429
produk name	\N	\N	produk sku 002	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	2	2025-09-01 06:22:22.98514	2025-09-01 06:22:22.985146
produk name	\N	\N	produk sku 004	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	3	2025-09-01 06:23:39.731396	2025-09-01 06:23:39.731404
produk name	\N	\N	produk sku 0040	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	4	2025-09-01 06:24:18.94598	2025-09-01 06:24:18.945988
kong test product	\N	\N	kong-test-001	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	6	2025-09-01 06:34:07.543861	2025-09-01 06:34:07.543867
follow redirect test	\N	\N	follow-redirect-002	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	7	2025-09-01 06:53:11.831978	2025-09-01 06:53:11.83199
final redirect test	\N	\N	final-redirect-001	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	8	2025-09-01 06:57:24.458915	2025-09-01 06:57:24.458922
trailing slash test	\N	\N	trailing-slash-001	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	9	2025-09-01 08:23:59.857038	2025-09-01 08:23:59.857047
explicit route test	\N	\N	explicit-route-001	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	10	2025-09-01 08:26:49.48196	2025-09-01 08:26:49.481968
trailing slash explicit test	\N	\N	trailing-slash-explicit-001	\N	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	11	2025-09-01 08:26:56.659842	2025-09-01 08:26:56.65985
Updated Test Product	\N	\N	TEST-001	\N	\N	\N	PHYSICAL	ACTIVE	99.99	\N	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	12	2025-09-03 04:26:44.656109	2025-09-03 04:26:58.91147
TEWT	\N	\N	343	4324	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	KILOGRAM	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	13	2025-09-03 04:28:03.431734	2025-09-03 04:28:03.43174
Ujung	\N	\N	3145	3141	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	METER	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	15	2025-09-03 05:56:43.980448	2025-09-03 05:56:43.980456
Pefdsgs	\N	\N	s23412	321412	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	METER	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	17	2025-09-03 09:40:07.233705	2025-09-03 09:40:07.233711
Test 102	\N	\N	23341	443	\N	\N	PHYSICAL	ACTIVE	\N	\N	USD	METER	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	18	2025-09-04 07:58:07.55394	2025-09-04 07:58:07.553946
43243333333	\N	\N	2453	34	\N	2	PHYSICAL	ACTIVE	\N	\N	USD	KILOGRAM	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	16	2025-09-03 08:10:01.623599	2025-09-13 09:17:39.190612
direct test product	\N	\N	direct-test-001	789	\N	\N	PHYSICAL	ACTIVE	900.00	800.00	USD	EACH	\N	kg	null	t	\N	\N	\N	\N	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	5	2025-09-01 06:33:58.60065	2025-09-14 22:59:22.211735
41412	\N	\N	123214	41	\N	3	PHYSICAL	ACTIVE	1.00	1.00	USD	KILOGRAM	\N	kg	null	t	\N	\N	0.00	0.00	\N	\N	\N	f	f	f	f	f	f	\N	\N	null	null	\N	null	null	t	\N	1	1.0.0	14	2025-09-03 05:47:26.675077	2025-09-15 08:51:14.154566
\.


--
-- Data for Name: receiving_line_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.receiving_line_items (receiving_record_id, product_id, product_variant_id, line_number, quantity_expected, quantity_received, quantity_accepted, quantity_rejected, quantity_damaged, unit_cost, total_cost, batch_number, serial_numbers, expiration_date, put_away_location_id, status, received_date, quality_check_required, quality_check_passed, quality_notes, inspected_by_user_id, inspected_at, rejection_reason, damage_description, notes, company_id, framework_version, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: receiving_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.receiving_records (receipt_number, source_document_type, source_document_id, source_document_number, supplier_id, supplier_invoice_number, supplier_delivery_note, warehouse_id, receiving_location_id, expected_date, received_date, scheduled_date, status, total_quantity_expected, total_quantity_received, total_value_expected, total_value_received, quality_inspection_required, quality_inspection_passed, quality_notes, received_by_user_id, approved_by_user_id, approved_at, carrier_name, tracking_number, freight_cost, notes, attachments, is_active, company_id, framework_version, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: stock_levels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_levels (product_id, product_variant_id, warehouse_location_id, quantity_on_hand, quantity_reserved, quantity_available, quantity_incoming, batch_number, serial_numbers, expiration_date, unit_cost, total_cost, cost_method, last_movement_date, last_movement_type, last_count_date, is_active, negative_stock_allowed, company_id, framework_version, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: stock_movements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_movements (product_id, product_variant_id, warehouse_location_id, from_location_id, to_location_id, movement_type, movement_date, quantity, unit_cost, total_cost, batch_number, serial_numbers, expiration_date, source_document_type, source_document_id, source_document_number, created_by_user_id, approved_by_user_id, approved_at, reference_number, notes, reason_code, quality_check_required, quality_check_passed, quality_notes, inspected_by_user_id, inspected_at, quantity_before, quantity_after, is_reversed, reversed_by_movement_id, reversed_at, movement_metadata, company_id, framework_version, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: warehouse_locations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_locations (warehouse_id, name, code, barcode, parent_location_id, location_type, level, position_x, position_y, position_z, max_weight_kg, max_volume_cbm, max_items, current_weight_kg, current_volume_cbm, current_items, allow_mixed_products, allow_mixed_batches, require_picking_confirmation, climate_controlled, temperature_min, temperature_max, humidity_min, humidity_max, pick_sequence, putaway_sequence, abc_classification, restricted_access, access_permissions, hazmat_approved, last_inspected_date, next_inspection_date, inspection_frequency_days, is_active, is_blocked, blocked_reason, blocked_until, notes, custom_attributes, company_id, framework_version, id, created_at, updated_at) FROM stdin;
1	Receiving Area	REC-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	1	2025-09-03 04:11:03.81463	2025-09-03 04:11:03.814638
1	Shipping Area	SHIP-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	2	2025-09-03 04:11:03.821933	2025-09-03 04:11:03.821945
1	General Storage	STOR-001	\N	\N	ZONE	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	3	2025-09-03 04:11:03.826639	2025-09-03 04:11:03.826647
1	Updated Test Location	TEST-LOC-001	\N	\N	BIN	0	\N	\N	\N	\N	\N	100	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	null	f	\N	\N	90	t	f	\N	\N	\N	null	1	1.0.0	4	2025-09-03 04:12:19.463302	2025-09-03 04:12:34.568858
2	Receiving Area	REC-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	5	2025-09-03 04:23:17.997752	2025-09-03 04:23:17.997761
2	Shipping Area	SHIP-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	6	2025-09-03 04:23:18.003584	2025-09-03 04:23:18.003593
2	General Storage	STOR-001	\N	\N	ZONE	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	7	2025-09-03 04:23:18.009312	2025-09-03 04:23:18.009325
3	Receiving Area	REC-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	8	2025-09-03 04:26:51.555613	2025-09-03 04:26:51.555628
3	Shipping Area	SHIP-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	9	2025-09-03 04:26:51.560989	2025-09-03 04:26:51.560996
3	General Storage	STOR-001	\N	\N	ZONE	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	10	2025-09-03 04:26:51.565615	2025-09-03 04:26:51.565621
4	Receiving Area	REC-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	11	2025-09-03 07:50:59.54056	2025-09-03 07:50:59.54057
4	Shipping Area	SHIP-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	12	2025-09-03 07:50:59.551828	2025-09-03 07:50:59.551837
4	General Storage	STOR-001	\N	\N	ZONE	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	13	2025-09-03 07:50:59.559876	2025-09-03 07:50:59.559885
5	Receiving Area	REC-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	14	2025-09-03 07:58:11.462283	2025-09-03 07:58:11.462289
5	Shipping Area	SHIP-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	15	2025-09-03 07:58:11.467287	2025-09-03 07:58:11.467297
5	General Storage	STOR-001	\N	\N	ZONE	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	16	2025-09-03 07:58:11.472156	2025-09-03 07:58:11.472162
6	Receiving Area	REC-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	17	2025-09-04 23:17:58.542745	2025-09-04 23:17:58.542751
6	Shipping Area	SHIP-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	18	2025-09-04 23:17:58.550888	2025-09-04 23:17:58.550895
6	General Storage	STOR-001	\N	\N	ZONE	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	19	2025-09-04 23:17:58.555214	2025-09-04 23:17:58.55522
7	Receiving Area	REC-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	20	2025-09-04 23:29:57.482124	2025-09-04 23:29:57.482138
7	Shipping Area	SHIP-001	\N	\N	STAGING	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	21	2025-09-04 23:29:57.486704	2025-09-04 23:29:57.486711
7	General Storage	STOR-001	\N	\N	ZONE	0	\N	\N	\N	\N	\N	\N	0.00	0.0000	0	t	t	f	f	\N	\N	\N	\N	0	0	\N	f	\N	f	\N	\N	90	t	f	\N	\N	\N	\N	1	1.0.0	22	2025-09-04 23:29:57.490911	2025-09-04 23:29:57.490918
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouses (name, code, description, warehouse_type, address_line_1, address_line_2, city, state_province, postal_code, country_code, phone, email, contact_person, latitude, longitude, timezone, operating_hours, currency_code, capabilities, total_area_sqm, storage_area_sqm, ceiling_height_m, dock_doors_count, default_cost_center, labor_cost_per_hour, storage_cost_per_sqm, allow_negative_stock, require_location_tracking, enable_cycle_counting, default_receiving_location_id, default_shipping_location_id, is_active, is_primary, warehouse_manager_user_id, last_cycle_count_date, company_id, framework_version, id, created_at, updated_at) FROM stdin;
Test Warehouse 2	TEST-002	\N	MAIN	\N	\N	\N	\N	\N	US	\N	\N	\N	\N	\N	UTC	null	USD	null	\N	\N	\N	\N	\N	\N	\N	f	t	t	5	6	t	f	\N	\N	1	1.0.0	2	2025-09-03 04:23:17.990298	2025-09-03 04:23:18.0194
Test Warehouse 5	TEST-005	\N	MAIN	\N	\N	\N	\N	\N	US	\N	\N	\N	\N	\N	UTC	null	USD	null	\N	\N	\N	\N	\N	\N	\N	f	t	t	11	12	t	f	\N	\N	1	1.0.0	4	2025-09-03 07:50:59.508901	2025-09-03 07:50:59.572609
Test Warehouse	TEST-WH	\N	MAIN	\N	\N	\N	\N	\N	US	\N	\N	\N	\N	\N	UTC	null	USD	null	\N	\N	\N	\N	\N	\N	\N	f	t	t	14	15	t	f	\N	\N	1	1.0.0	5	2025-09-03 07:58:11.457225	2025-09-03 07:58:11.477789
Updated Test Warehouse	TEST-001	\N	MAIN	\N	\N	New York	\N	\N	US	\N	\N	\N	\N	\N	UTC	null	USD	null	\N	\N	\N	\N	\N	\N	\N	f	t	t	1	2	t	f	\N	\N	1	1.0.0	1	2025-09-03 04:11:03.775484	2025-09-03 08:09:33.403854
Test 102	001	\N	MAIN	\N	\N	\N	\N	\N	US	\N	\N	\N	\N	\N	UTC	null	USD	null	\N	\N	\N	\N	\N	\N	\N	f	t	t	17	18	t	f	\N	\N	1	1.0.0	6	2025-09-04 23:17:58.51348	2025-09-04 23:17:58.565085
Test Warehouse 3	TEST-003	\N	MAIN	\N	\N	\N	\N	\N	US	\N	\N	\N	\N	\N	UTC	null	USD	null	\N	\N	\N	\N	\N	\N	\N	f	t	t	8	9	t	f	\N	\N	1	1.0.0	3	2025-09-03 04:26:51.548488	2025-09-15 02:52:10.183291
999	999	\N	MAIN	\N	\N	\N	\N	\N	US	\N	\N	\N	\N	\N	UTC	null	USD	null	\N	\N	\N	\N	\N	\N	\N	f	t	t	20	21	t	f	\N	\N	1	1.0.0	7	2025-09-04 23:29:57.477781	2025-09-15 08:52:08.795673
\.


--
-- Name: product_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_categories_id_seq', 13, true);


--
-- Name: product_variants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_variants_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 18, true);


--
-- Name: receiving_line_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.receiving_line_items_id_seq', 1, false);


--
-- Name: receiving_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.receiving_records_id_seq', 1, false);


--
-- Name: stock_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_levels_id_seq', 1, false);


--
-- Name: stock_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_movements_id_seq', 1, false);


--
-- Name: warehouse_locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouse_locations_id_seq', 22, true);


--
-- Name: warehouses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouses_id_seq', 7, true);


--
-- Name: product_categories product_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_pkey PRIMARY KEY (id);


--
-- Name: product_variants product_variants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_variants
    ADD CONSTRAINT product_variants_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: receiving_line_items receiving_line_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_line_items
    ADD CONSTRAINT receiving_line_items_pkey PRIMARY KEY (id);


--
-- Name: receiving_records receiving_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_records
    ADD CONSTRAINT receiving_records_pkey PRIMARY KEY (id);


--
-- Name: stock_levels stock_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT stock_levels_pkey PRIMARY KEY (id);


--
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (id);


--
-- Name: warehouse_locations warehouse_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations
    ADD CONSTRAINT warehouse_locations_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: ix_product_categories_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_code ON public.product_categories USING btree (code);


--
-- Name: ix_product_categories_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_company_id ON public.product_categories USING btree (company_id);


--
-- Name: ix_product_categories_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_id ON public.product_categories USING btree (id);


--
-- Name: ix_product_categories_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_is_active ON public.product_categories USING btree (is_active);


--
-- Name: ix_product_categories_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_name ON public.product_categories USING btree (name);


--
-- Name: ix_product_categories_parent_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_parent_category_id ON public.product_categories USING btree (parent_category_id);


--
-- Name: ix_product_categories_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_categories_slug ON public.product_categories USING btree (slug);


--
-- Name: ix_product_variants_barcode; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_variants_barcode ON public.product_variants USING btree (barcode);


--
-- Name: ix_product_variants_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_variants_company_id ON public.product_variants USING btree (company_id);


--
-- Name: ix_product_variants_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_variants_id ON public.product_variants USING btree (id);


--
-- Name: ix_product_variants_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_variants_is_active ON public.product_variants USING btree (is_active);


--
-- Name: ix_product_variants_parent_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_product_variants_parent_product_id ON public.product_variants USING btree (parent_product_id);


--
-- Name: ix_product_variants_sku; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_product_variants_sku ON public.product_variants USING btree (sku);


--
-- Name: ix_products_barcode; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_barcode ON public.products USING btree (barcode);


--
-- Name: ix_products_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_category_id ON public.products USING btree (category_id);


--
-- Name: ix_products_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_company_id ON public.products USING btree (company_id);


--
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_id ON public.products USING btree (id);


--
-- Name: ix_products_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_is_active ON public.products USING btree (is_active);


--
-- Name: ix_products_manufacturer_part_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_manufacturer_part_number ON public.products USING btree (manufacturer_part_number);


--
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_name ON public.products USING btree (name);


--
-- Name: ix_products_primary_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_primary_supplier_id ON public.products USING btree (primary_supplier_id);


--
-- Name: ix_products_product_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_product_type ON public.products USING btree (product_type);


--
-- Name: ix_products_sku; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_products_sku ON public.products USING btree (sku);


--
-- Name: ix_products_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_status ON public.products USING btree (status);


--
-- Name: ix_receiving_line_items_batch_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_batch_number ON public.receiving_line_items USING btree (batch_number);


--
-- Name: ix_receiving_line_items_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_company_id ON public.receiving_line_items USING btree (company_id);


--
-- Name: ix_receiving_line_items_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_id ON public.receiving_line_items USING btree (id);


--
-- Name: ix_receiving_line_items_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_product_id ON public.receiving_line_items USING btree (product_id);


--
-- Name: ix_receiving_line_items_product_variant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_product_variant_id ON public.receiving_line_items USING btree (product_variant_id);


--
-- Name: ix_receiving_line_items_put_away_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_put_away_location_id ON public.receiving_line_items USING btree (put_away_location_id);


--
-- Name: ix_receiving_line_items_receiving_record_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_receiving_record_id ON public.receiving_line_items USING btree (receiving_record_id);


--
-- Name: ix_receiving_line_items_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_line_items_status ON public.receiving_line_items USING btree (status);


--
-- Name: ix_receiving_records_approved_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_approved_by_user_id ON public.receiving_records USING btree (approved_by_user_id);


--
-- Name: ix_receiving_records_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_company_id ON public.receiving_records USING btree (company_id);


--
-- Name: ix_receiving_records_expected_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_expected_date ON public.receiving_records USING btree (expected_date);


--
-- Name: ix_receiving_records_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_id ON public.receiving_records USING btree (id);


--
-- Name: ix_receiving_records_receipt_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_receiving_records_receipt_number ON public.receiving_records USING btree (receipt_number);


--
-- Name: ix_receiving_records_received_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_received_by_user_id ON public.receiving_records USING btree (received_by_user_id);


--
-- Name: ix_receiving_records_received_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_received_date ON public.receiving_records USING btree (received_date);


--
-- Name: ix_receiving_records_receiving_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_receiving_location_id ON public.receiving_records USING btree (receiving_location_id);


--
-- Name: ix_receiving_records_source_document_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_source_document_id ON public.receiving_records USING btree (source_document_id);


--
-- Name: ix_receiving_records_source_document_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_source_document_number ON public.receiving_records USING btree (source_document_number);


--
-- Name: ix_receiving_records_source_document_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_source_document_type ON public.receiving_records USING btree (source_document_type);


--
-- Name: ix_receiving_records_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_status ON public.receiving_records USING btree (status);


--
-- Name: ix_receiving_records_supplier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_supplier_id ON public.receiving_records USING btree (supplier_id);


--
-- Name: ix_receiving_records_supplier_invoice_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_supplier_invoice_number ON public.receiving_records USING btree (supplier_invoice_number);


--
-- Name: ix_receiving_records_tracking_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_tracking_number ON public.receiving_records USING btree (tracking_number);


--
-- Name: ix_receiving_records_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_receiving_records_warehouse_id ON public.receiving_records USING btree (warehouse_id);


--
-- Name: ix_stock_levels_batch_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_batch_number ON public.stock_levels USING btree (batch_number);


--
-- Name: ix_stock_levels_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_company_id ON public.stock_levels USING btree (company_id);


--
-- Name: ix_stock_levels_expiration_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_expiration_date ON public.stock_levels USING btree (expiration_date);


--
-- Name: ix_stock_levels_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_id ON public.stock_levels USING btree (id);


--
-- Name: ix_stock_levels_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_product_id ON public.stock_levels USING btree (product_id);


--
-- Name: ix_stock_levels_product_variant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_product_variant_id ON public.stock_levels USING btree (product_variant_id);


--
-- Name: ix_stock_levels_warehouse_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_levels_warehouse_location_id ON public.stock_levels USING btree (warehouse_location_id);


--
-- Name: ix_stock_movements_approved_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_approved_by_user_id ON public.stock_movements USING btree (approved_by_user_id);


--
-- Name: ix_stock_movements_batch_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_batch_number ON public.stock_movements USING btree (batch_number);


--
-- Name: ix_stock_movements_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_company_id ON public.stock_movements USING btree (company_id);


--
-- Name: ix_stock_movements_created_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_created_by_user_id ON public.stock_movements USING btree (created_by_user_id);


--
-- Name: ix_stock_movements_from_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_from_location_id ON public.stock_movements USING btree (from_location_id);


--
-- Name: ix_stock_movements_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_id ON public.stock_movements USING btree (id);


--
-- Name: ix_stock_movements_movement_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_movement_date ON public.stock_movements USING btree (movement_date);


--
-- Name: ix_stock_movements_movement_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_movement_type ON public.stock_movements USING btree (movement_type);


--
-- Name: ix_stock_movements_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_product_id ON public.stock_movements USING btree (product_id);


--
-- Name: ix_stock_movements_product_variant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_product_variant_id ON public.stock_movements USING btree (product_variant_id);


--
-- Name: ix_stock_movements_reason_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_reason_code ON public.stock_movements USING btree (reason_code);


--
-- Name: ix_stock_movements_reference_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_reference_number ON public.stock_movements USING btree (reference_number);


--
-- Name: ix_stock_movements_source_document_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_source_document_id ON public.stock_movements USING btree (source_document_id);


--
-- Name: ix_stock_movements_source_document_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_source_document_number ON public.stock_movements USING btree (source_document_number);


--
-- Name: ix_stock_movements_source_document_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_source_document_type ON public.stock_movements USING btree (source_document_type);


--
-- Name: ix_stock_movements_to_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_to_location_id ON public.stock_movements USING btree (to_location_id);


--
-- Name: ix_stock_movements_warehouse_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_warehouse_location_id ON public.stock_movements USING btree (warehouse_location_id);


--
-- Name: ix_warehouse_locations_barcode; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_warehouse_locations_barcode ON public.warehouse_locations USING btree (barcode);


--
-- Name: ix_warehouse_locations_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_code ON public.warehouse_locations USING btree (code);


--
-- Name: ix_warehouse_locations_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_company_id ON public.warehouse_locations USING btree (company_id);


--
-- Name: ix_warehouse_locations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_id ON public.warehouse_locations USING btree (id);


--
-- Name: ix_warehouse_locations_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_is_active ON public.warehouse_locations USING btree (is_active);


--
-- Name: ix_warehouse_locations_is_blocked; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_is_blocked ON public.warehouse_locations USING btree (is_blocked);


--
-- Name: ix_warehouse_locations_location_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_location_type ON public.warehouse_locations USING btree (location_type);


--
-- Name: ix_warehouse_locations_parent_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_parent_location_id ON public.warehouse_locations USING btree (parent_location_id);


--
-- Name: ix_warehouse_locations_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_warehouse_id ON public.warehouse_locations USING btree (warehouse_id);


--
-- Name: ix_warehouses_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_warehouses_code ON public.warehouses USING btree (code);


--
-- Name: ix_warehouses_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_company_id ON public.warehouses USING btree (company_id);


--
-- Name: ix_warehouses_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_id ON public.warehouses USING btree (id);


--
-- Name: ix_warehouses_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_is_active ON public.warehouses USING btree (is_active);


--
-- Name: ix_warehouses_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_name ON public.warehouses USING btree (name);


--
-- Name: ix_warehouses_warehouse_manager_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_warehouse_manager_user_id ON public.warehouses USING btree (warehouse_manager_user_id);


--
-- Name: ix_warehouses_warehouse_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouses_warehouse_type ON public.warehouses USING btree (warehouse_type);


--
-- Name: product_categories product_categories_parent_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES public.product_categories(id) ON DELETE SET NULL;


--
-- Name: product_variants product_variants_parent_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_variants
    ADD CONSTRAINT product_variants_parent_product_id_fkey FOREIGN KEY (parent_product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.product_categories(id) ON DELETE SET NULL;


--
-- Name: receiving_line_items receiving_line_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_line_items
    ADD CONSTRAINT receiving_line_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: receiving_line_items receiving_line_items_product_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_line_items
    ADD CONSTRAINT receiving_line_items_product_variant_id_fkey FOREIGN KEY (product_variant_id) REFERENCES public.product_variants(id) ON DELETE CASCADE;


--
-- Name: receiving_line_items receiving_line_items_put_away_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_line_items
    ADD CONSTRAINT receiving_line_items_put_away_location_id_fkey FOREIGN KEY (put_away_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: receiving_line_items receiving_line_items_receiving_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_line_items
    ADD CONSTRAINT receiving_line_items_receiving_record_id_fkey FOREIGN KEY (receiving_record_id) REFERENCES public.receiving_records(id) ON DELETE CASCADE;


--
-- Name: receiving_records receiving_records_receiving_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_records
    ADD CONSTRAINT receiving_records_receiving_location_id_fkey FOREIGN KEY (receiving_location_id) REFERENCES public.warehouse_locations(id) ON DELETE RESTRICT;


--
-- Name: receiving_records receiving_records_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receiving_records
    ADD CONSTRAINT receiving_records_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE RESTRICT;


--
-- Name: stock_levels stock_levels_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT stock_levels_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: stock_levels stock_levels_product_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT stock_levels_product_variant_id_fkey FOREIGN KEY (product_variant_id) REFERENCES public.product_variants(id) ON DELETE CASCADE;


--
-- Name: stock_levels stock_levels_warehouse_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_levels
    ADD CONSTRAINT stock_levels_warehouse_location_id_fkey FOREIGN KEY (warehouse_location_id) REFERENCES public.warehouse_locations(id) ON DELETE CASCADE;


--
-- Name: stock_movements stock_movements_from_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_from_location_id_fkey FOREIGN KEY (from_location_id) REFERENCES public.warehouse_locations(id);


--
-- Name: stock_movements stock_movements_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: stock_movements stock_movements_product_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_product_variant_id_fkey FOREIGN KEY (product_variant_id) REFERENCES public.product_variants(id) ON DELETE CASCADE;


--
-- Name: stock_movements stock_movements_reversed_by_movement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_reversed_by_movement_id_fkey FOREIGN KEY (reversed_by_movement_id) REFERENCES public.stock_movements(id);


--
-- Name: stock_movements stock_movements_to_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_to_location_id_fkey FOREIGN KEY (to_location_id) REFERENCES public.warehouse_locations(id);


--
-- Name: stock_movements stock_movements_warehouse_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_warehouse_location_id_fkey FOREIGN KEY (warehouse_location_id) REFERENCES public.warehouse_locations(id) ON DELETE CASCADE;


--
-- Name: warehouse_locations warehouse_locations_parent_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations
    ADD CONSTRAINT warehouse_locations_parent_location_id_fkey FOREIGN KEY (parent_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: warehouse_locations warehouse_locations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations
    ADD CONSTRAINT warehouse_locations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: warehouses warehouses_default_receiving_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_default_receiving_location_id_fkey FOREIGN KEY (default_receiving_location_id) REFERENCES public.warehouse_locations(id);


--
-- Name: warehouses warehouses_default_shipping_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_default_shipping_location_id_fkey FOREIGN KEY (default_shipping_location_id) REFERENCES public.warehouse_locations(id);


--
-- PostgreSQL database dump complete
--

\unrestrict D0tupRLU5OFHJ8OmgxvqmhT940Wd5d7bmafC63zlFaNr1C4KgEdUROYKTOO16aA

