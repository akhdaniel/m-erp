--
-- PostgreSQL database dump
--

\restrict QUvLVesz3tm6u9X7CgDryFYTuBhV1kY3Xe2p8MjuO93kRF95ABjWaCEVuMo6TEq

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
-- Name: menu_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_items (
    code character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    parent_id integer,
    order_index integer NOT NULL,
    level integer NOT NULL,
    url character varying(500),
    icon character varying(100),
    target character varying(20),
    item_type character varying(20) NOT NULL,
    is_external boolean NOT NULL,
    is_active boolean NOT NULL,
    is_visible boolean NOT NULL,
    required_permission character varying(100),
    required_role_level integer,
    metadata_info json,
    css_class character varying(255),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    badge_text character varying(50),
    badge_class character varying(100),
    CONSTRAINT menu_items_level_check CHECK ((level >= 0)),
    CONSTRAINT menu_items_order_check CHECK ((order_index >= 0)),
    CONSTRAINT menu_items_type_check CHECK (((item_type)::text = ANY ((ARRAY['link'::character varying, 'divider'::character varying, 'header'::character varying, 'dropdown'::character varying])::text[])))
);


ALTER TABLE public.menu_items OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.menu_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.menu_items_id_seq OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.menu_items_id_seq OWNED BY public.menu_items.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    code character varying(100) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    category character varying(50) NOT NULL,
    action character varying(50) NOT NULL,
    is_active boolean NOT NULL,
    is_system boolean NOT NULL,
    metadata_info json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    code character varying(50) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    is_active boolean NOT NULL,
    is_system boolean NOT NULL,
    is_default boolean NOT NULL,
    level integer NOT NULL,
    metadata_info json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: menu_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items ALTER COLUMN id SET DEFAULT nextval('public.menu_items_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
c13ab8992f1f
\.


--
-- Data for Name: menu_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_items (code, title, description, parent_id, order_index, level, url, icon, target, item_type, is_external, is_active, is_visible, required_permission, required_role_level, metadata_info, css_class, id, created_at, updated_at, badge_text, badge_class) FROM stdin;
products_catalog	Products	Product catalog and management	1	10	1	/inventory/products	fas fa-box	_self	link	f	t	t	products.view	\N	{}	\N	2	2025-08-24 05:42:55.991705+00	2025-08-24 05:42:55.991705+00	\N	\N
stock_movements	Stock Movements	View stock movements and adjustments	1	30	1	/inventory/stock-movements	fas fa-arrows-alt-h	_self	link	f	t	t	stock.view	\N	{}	\N	4	2025-08-24 05:42:55.991705+00	2025-08-24 05:42:55.991705+00	\N	\N
stock_levels	Stock Levels	Current stock levels and alerts	1	40	1	/inventory/stock-levels	fas fa-chart-line	_self	link	f	t	t	stock.view	\N	{}	\N	5	2025-08-24 05:42:55.991705+00	2025-08-24 05:42:55.991705+00	\N	\N
suppliers_management	Suppliers	Supplier and vendor management	1	70	1	/inventory/suppliers	fas fa-truck	_self	link	f	t	t	partners.view	\N	{}	\N	8	2025-08-24 05:42:55.991705+00	2025-08-24 05:42:55.991705+00	\N	\N
settings	Settings	System configuration and settings	\N	100	0	/settings	fas fa-cog	_self	dropdown	f	t	t	settings.access	\N	{}	\N	16	2025-08-24 06:02:26.092549+00	2025-08-24 06:02:26.092549+00	\N	\N
menu_configuration	Menu Configuration	View and configure all service menus	16	10	1	/settings/menus	fas fa-bars	_self	link	f	t	t	menu.configuration	\N	{}	\N	17	2025-08-24 06:02:26.092549+00	2025-08-24 06:02:26.092549+00	\N	\N
inventory_products	Products	Product Management	1	2	1	/inventory/products	box	_self	link	f	t	t	view_products	\N	{}	\N	22	2025-09-02 05:22:03.916932+00	2025-09-02 05:22:03.916932+00	\N	\N
inventory_dashboard	Dashboard	Inventory Dashboard	1	1	1	/inventory/dashboard	chart-bar	_self	link	f	t	t	access_inventory	\N	{}	\N	21	2025-09-02 05:22:03.626295+00	2025-09-11 04:19:56.222949+00	\N	\N
inventory_stock	Stock	Stock Management	1	4	1	/inventory/stock	layers	_self	link	f	t	t	view_stock	\N	{}	\N	23	2025-09-02 05:22:04.210855+00	2025-09-11 04:19:57.250721+00	\N	\N
warehouses_management	Warehouses	Warehouse and location management	28	1	1	/inventory/warehouses	fas fa-warehouse	_self	link	f	t	t	warehouses.view	\N	{}	\N	6	2025-08-24 05:42:55.991705+00	2025-09-15 08:17:19.075544+00	\N	\N
inventory_receiving	Receiving	Receiving Operations	1	6	1	/inventory/receiving	download	_self	link	f	t	t	process_receiving	\N	{}	\N	7	2025-08-24 05:42:55.991705+00	2025-09-11 04:19:57.98015+00	\N	\N
inventory_reports	Reports	Inventory Reports	1	7	1	/inventory/reports	file-text	_self	link	f	t	t	view_inventory_reports	\N	{}	\N	25	2025-09-02 05:22:05.067821+00	2025-09-11 04:19:58.295782+00	\N	\N
inventory_categories	Categories	Product Categories	28	3	2	/inventory/categories	tag	_self	link	f	t	t	view_products	\N	{}	\N	30	2025-09-15 08:17:18.065777+00	2025-09-15 08:17:19.384723+00	\N	\N
inventory_management	Inventory	Inventory Management	\N	3	0	/inventory/dashboard	warehouse	_self	dropdown	f	t	t	access_inventory	\N	{}	\N	1	2025-08-24 05:42:55.991705+00	2025-09-14 21:25:47.754351+00	\N	\N
analytic_reports	Analytic Reports	Inventory Analytic Reports	25	1	2	/inventory/reports/analytics	file-text	_self	link	f	t	t	view_inventory_reports	\N	{}	\N	26	2025-09-02 05:22:05.360839+00	2025-09-15 04:47:17.443151+00	\N	\N
inventory_settings	Settings	Inventory Settings	1	100	1	#	cogs	_self	dropdown	f	t	t	view_inventory_reports	\N	{}	\N	28	2025-09-15 04:24:39.927254+00	2025-09-15 08:18:12.741431+00	\N	\N
inventory_warehouses	Warehouses	Warehouse Management	28	5	2	/inventory/warehouses	building	_self	link	f	t	t	view_warehouses	\N	{}	\N	29	2025-09-15 08:17:17.919574+00	2025-09-15 08:18:12.8843+00	\N	\N
product_categories	Product Categories	Manage product categories and classification	28	0	1	/inventory/categories	fas fa-sitemap	_self	link	f	t	t	products.view	\N	{}	\N	3	2025-08-24 05:42:55.991705+00	2025-09-15 08:17:19.075544+00	\N	\N
sales_pricing	Pricing Rules	Pricing Management	34	3	1	/sales/pricing	dollar-sign	_self	link	f	t	t	view_pricing	\N	{}	\N	35	2025-09-19 03:13:57.294707+00	2025-09-19 03:24:40.05474+00	\N	\N
sales_management	Sales	Sales Management	\N	2	0	#	shopping-cart	_self	dropdown	f	t	t	access_sales	\N	{}	\N	9	2025-08-24 05:42:56.028112+00	2025-09-19 03:13:56.238977+00	\N	\N
sales_transactions	Transactions	All Sales Transactions	9	1	1	/sales/transactions	file-text	_self	link	f	t	t	access_sales	\N	{}	\N	36	2025-09-19 08:40:24.337625+00	2025-09-19 08:40:25.640607+00	\N	\N
sales_dashboard	Dashboard	Sales Dashboard Overview	9	0	1	/sales/dashboard	grid-3x3	_self	link	f	t	t	access_sales	\N	{}	\N	31	2025-09-19 03:13:56.3894+00	2025-09-19 03:13:57.585977+00	\N	\N
sales_invoices	Invoices	Sales invoices and billing management	9	8	1	/sales/invoices	fas fa-file-invoice	_self	link	f	t	t	invoices.view	\N	{}	\N	14	2025-08-24 05:42:56.028112+00	2025-09-19 03:13:58.271902+00	\N	\N
sales_settings	Settings	Sales Settings and Configurations	9	100	1	/sales/settings	cogs	_self	dropdown	f	t	t	access_sales	\N	{}	\N	34	2025-09-19 03:13:57.128639+00	2025-09-19 22:17:36.068378+00	\N	\N
sales_quotes	Quotations	Quotation Management	9	2	1	/sales/transactions?state=draft,quote_pending_approval,quote_approved,quote_sent,quote_accepted,quote_rejected,quote_expired	file-text	_self	link	f	t	t	manage_quotes	\N	{}	\N	32	2025-09-19 03:13:56.557754+00	2025-09-19 08:40:24.483261+00	\N	\N
sales_customers	Customers	Customer Management	9	4	1	/sales/customers	users	_self	link	f	t	t	access_sales	\N	{}	\N	33	2025-09-19 03:13:56.842291+00	2025-09-19 03:13:58.271902+00	\N	\N
sales_analytics	Analytics	Sales Analytics & Reports	9	5	1	/sales/analytics	bar-chart	_self	link	f	t	t	sales_analytics	\N	{}	\N	15	2025-08-24 05:42:56.028112+00	2025-09-19 03:24:39.770144+00	\N	\N
sales_orders	Orders	Sales Order Management	9	3	1	/sales/transactions?state=order_pending,order_confirmed,order_in_production,order_ready_to_ship,order_partially_shipped,order_shipped,order_delivered,order_completed,order_cancelled,order_on_hold	shopping-bag	_self	link	f	t	t	manage_orders	\N	{}	\N	11	2025-08-24 05:42:56.028112+00	2025-09-19 08:40:24.62817+00	\N	\N
sales_products	Products	Product catalog and inventory for sales	9	5	1	/inventory/products	fas fa-tags	_self	link	f	t	t	access_sales	\N	{}	\N	13	2025-08-24 05:42:56.028112+00	2025-10-11 22:16:14.627988+00	\N	\N
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (code, name, description, category, action, is_active, is_system, metadata_info, id, created_at, updated_at) FROM stdin;
inventory.access	Inventory Management	Access to inventory management system	inventory	access	t	f	{}	1	2025-08-24 05:42:55.952861+00	2025-08-24 05:42:55.952861+00
products.view	View Products	View product catalog and details	products	read	t	f	{}	2	2025-08-24 05:42:55.952861+00	2025-08-24 05:42:55.952861+00
products.manage	Manage Products	Create, update, and delete products	products	write	t	f	{}	3	2025-08-24 05:42:55.952861+00	2025-08-24 05:42:55.952861+00
stock.view	View Stock	View stock levels and movements	stock	read	t	f	{}	4	2025-08-24 05:42:55.952861+00	2025-08-24 05:42:55.952861+00
warehouses.view	View Warehouses	View warehouse and location information	warehouses	read	t	f	{}	5	2025-08-24 05:42:55.952861+00	2025-08-24 05:42:55.952861+00
receiving.view	View Receiving	View inbound receiving operations	receiving	read	t	f	{}	6	2025-08-24 05:42:55.952861+00	2025-08-24 05:42:55.952861+00
sales.access	Sales Management	Access to sales management system	sales	access	t	f	{}	7	2025-08-24 05:42:56.013899+00	2025-08-24 05:42:56.013899+00
quotes.view	View Quotations	View sales quotations and proposals	quotes	read	t	f	{}	8	2025-08-24 05:42:56.013899+00	2025-08-24 05:42:56.013899+00
orders.view	View Orders	View sales orders and processing	orders	read	t	f	{}	9	2025-08-24 05:42:56.013899+00	2025-08-24 05:42:56.013899+00
customers.view	View Customers	View customer accounts and details	customers	read	t	f	{}	10	2025-08-24 05:42:56.013899+00	2025-08-24 05:42:56.013899+00
invoices.view	View Invoices	View customer invoices	invoices	read	t	f	{}	11	2025-08-24 05:42:56.013899+00	2025-08-24 05:42:56.013899+00
settings.access	Settings Access	Access to system settings	settings	access	t	f	{}	12	2025-08-24 06:02:26.078518+00	2025-08-24 06:02:26.078518+00
menu.configuration	Menu Configuration	Configure and manage menu items	menu	manage	t	f	{}	13	2025-08-24 06:02:26.078518+00	2025-08-24 06:02:26.078518+00
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_id, permission_id) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (code, name, description, is_active, is_system, is_default, level, metadata_info, id, created_at, updated_at) FROM stdin;
\.


--
-- Name: menu_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.menu_items_id_seq', 36, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 13, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: menu_items menu_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT menu_items_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_category_action_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_category_action_unique UNIQUE (category, action);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: ix_menu_items_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_menu_items_code ON public.menu_items USING btree (code);


--
-- Name: ix_menu_items_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_menu_items_id ON public.menu_items USING btree (id);


--
-- Name: ix_menu_items_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_menu_items_is_active ON public.menu_items USING btree (is_active);


--
-- Name: ix_menu_items_parent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_menu_items_parent_id ON public.menu_items USING btree (parent_id);


--
-- Name: ix_permissions_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_action ON public.permissions USING btree (action);


--
-- Name: ix_permissions_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_category ON public.permissions USING btree (category);


--
-- Name: ix_permissions_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_code ON public.permissions USING btree (code);


--
-- Name: ix_permissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_id ON public.permissions USING btree (id);


--
-- Name: ix_permissions_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_is_active ON public.permissions USING btree (is_active);


--
-- Name: ix_roles_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_code ON public.roles USING btree (code);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_is_active ON public.roles USING btree (is_active);


--
-- Name: menu_items menu_items_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT menu_items_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.menu_items(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict QUvLVesz3tm6u9X7CgDryFYTuBhV1kY3Xe2p8MjuO93kRF95ABjWaCEVuMo6TEq

