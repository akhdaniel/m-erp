--
-- PostgreSQL database dump
--

\restrict lyT7tMc4rUEd1dZIvzG4ZeP9NzTM3LveqrhfiJHmckOUUe6ZrwLGAL5ZrdeaKrE

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
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    action character varying(100) NOT NULL,
    severity character varying(20) NOT NULL,
    description character varying(500) NOT NULL,
    user_id integer,
    target_user_id integer,
    session_id character varying(255),
    request_id character varying(255),
    service_id integer,
    service_name character varying(100),
    ip_address character varying(45),
    user_agent text,
    client_info json,
    endpoint character varying(255),
    http_method character varying(10),
    request_data json,
    response_status integer,
    metadata json,
    tags json,
    success boolean NOT NULL,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: password_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_history (
    id integer NOT NULL,
    user_id integer NOT NULL,
    password_hash character varying NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.password_history OWNER TO postgres;

--
-- Name: password_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.password_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.password_history_id_seq OWNER TO postgres;

--
-- Name: password_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.password_history_id_seq OWNED BY public.password_history.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(255),
    permissions json NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
-- Name: service_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_tokens (
    id integer NOT NULL,
    service_id integer NOT NULL,
    token_hash character varying(255) NOT NULL,
    scopes json NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_revoked boolean NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    revoked_at timestamp with time zone
);


ALTER TABLE public.service_tokens OWNER TO postgres;

--
-- Name: service_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_tokens_id_seq OWNER TO postgres;

--
-- Name: service_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_tokens_id_seq OWNED BY public.service_tokens.id;


--
-- Name: services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.services (
    id integer NOT NULL,
    service_name character varying(100) NOT NULL,
    service_description character varying(500) NOT NULL,
    service_secret_hash character varying(255) NOT NULL,
    allowed_scopes json NOT NULL,
    callback_urls json,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_used timestamp with time zone
);


ALTER TABLE public.services OWNER TO postgres;

--
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.services_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.services_id_seq OWNER TO postgres;

--
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.services_id_seq OWNED BY public.services.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    assigned_by integer
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_roles_id_seq OWNER TO postgres;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    refresh_token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ip_address character varying(45),
    user_agent character varying(500),
    is_revoked boolean NOT NULL
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_id_seq OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    is_active boolean NOT NULL,
    is_verified boolean NOT NULL,
    is_superuser boolean NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login timestamp with time zone,
    deleted_at timestamp with time zone,
    failed_login_attempts integer DEFAULT 0 NOT NULL,
    locked_until timestamp with time zone,
    last_failed_login timestamp with time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: password_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_history ALTER COLUMN id SET DEFAULT nextval('public.password_history_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: service_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_tokens ALTER COLUMN id SET DEFAULT nextval('public.service_tokens_id_seq'::regclass);


--
-- Name: services id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services ALTER COLUMN id SET DEFAULT nextval('public.services_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
a1b2c3d4e5f6
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, action, severity, description, user_id, target_user_id, session_id, request_id, service_id, service_name, ip_address, user_agent, client_info, endpoint, http_method, request_data, response_status, metadata, tags, success, error_message, created_at) FROM stdin;
1	login_success	low	User successfully authenticated using password	1	\N	\N	3c1a7471-7cd6-4396-8711-02a5c6625673	\N	\N	172.20.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	\N	["authentication", "success"]	t	\N	2025-08-23 04:51:03.034117+00
2	login_success	low	User successfully authenticated using password	1	\N	\N	91040567-8100-4f90-9b54-db9828c9fd8a	\N	\N	172.20.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	\N	["authentication", "success"]	t	\N	2025-08-23 04:51:33.946285+00
3	login_success	low	User successfully authenticated using password	1	\N	\N	7c40325c-3202-4754-94ab-767b0868bad0	\N	\N	172.20.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-23 07:34:15.915954+00
4	login_success	low	User successfully authenticated using password	1	\N	\N	504e6e55-1698-41a0-b7e1-0ded470d2f01	\N	\N	172.20.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-23 07:58:21.141857+00
5	login_success	low	User successfully authenticated using password	1	\N	\N	b4f74cc7-9fb0-44c1-a78d-eb2e722b2ff9	\N	\N	172.20.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-23 08:05:22.729882+00
6	login_success	low	User successfully authenticated using password	1	\N	\N	00e0f825-449f-4fa0-8e2e-5ee883e240db	\N	\N	172.20.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-23 08:06:08.6394+00
7	login_success	low	User successfully authenticated using password	1	\N	\N	e8366e1a-e22c-445e-a075-ced705318d4d	\N	\N	172.19.0.16	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 01:08:25.090586+00
8	login_success	low	User successfully authenticated using password	1	\N	\N	64fee1c8-f0e8-4a0b-b38e-ecddb9d1052e	\N	\N	172.19.0.16	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 01:24:43.456932+00
9	login_success	low	User successfully authenticated using password	1	\N	\N	04dd2200-e6f5-457e-b596-fe3571ea9b77	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 01:46:48.150975+00
10	login_success	low	User successfully authenticated using password	1	\N	\N	bbaaa20e-4df1-40a9-843a-57dd4fc3fdfb	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 05:33:47.426057+00
11	login_success	low	User successfully authenticated using password	1	\N	\N	6718e015-a34d-4df5-bc72-f2fbc5479849	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 05:58:11.558514+00
12	login_success	low	User successfully authenticated using password	1	\N	\N	844ae4c0-556b-4e04-8016-7742a2456eb3	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 05:59:24.758297+00
13	login_success	low	User successfully authenticated using password	1	\N	\N	3d3e345f-f981-4f05-9200-802e6804f42c	\N	\N	172.19.0.19	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 06:22:39.516397+00
14	login_success	low	User successfully authenticated using password	1	\N	\N	12e7491f-d184-4373-9b34-04e52f9dc30d	\N	\N	172.19.0.19	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 06:23:26.594585+00
15	login_success	low	User successfully authenticated using password	1	\N	\N	20978cf7-bbfa-4305-8521-e03cdea3b7b3	\N	\N	172.19.0.19	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 06:23:37.316944+00
16	login_success	low	User successfully authenticated using password	1	\N	\N	8f77e9d1-86a1-4c38-93bc-3b3091f637e1	\N	\N	172.19.0.19	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 06:25:22.605423+00
17	login_success	low	User successfully authenticated using password	1	\N	\N	18885865-9424-4bf9-9543-4e3907cbc03c	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 06:29:28.076864+00
18	login_success	low	User successfully authenticated using password	1	\N	\N	71df0dbe-afbc-4a19-828c-dd22e4643222	\N	\N	172.19.0.19	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 06:29:40.706371+00
19	login_success	low	User successfully authenticated using password	1	\N	\N	071db40a-dbbe-4cd9-b482-1a10495f8c2d	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 06:49:33.816999+00
20	login_success	low	User successfully authenticated using password	1	\N	\N	a849fe39-5b60-4eeb-8090-dabce6cf21f7	\N	\N	172.19.0.16	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 07:05:55.24326+00
21	login_success	low	User successfully authenticated using password	1	\N	\N	f19e9c73-9a51-48aa-9788-2b4767f5837d	\N	\N	172.19.0.16	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 07:06:03.591452+00
22	login_success	low	User successfully authenticated using password	1	\N	\N	2d8a4f12-e8d1-4b8a-9f8a-ecac06c4c82c	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 07:14:14.899223+00
23	login_success	low	User successfully authenticated using password	1	\N	\N	12012ba8-d797-4c3c-9f1c-739a4986abe3	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 09:47:43.324412+00
24	login_success	low	User successfully authenticated using password	1	\N	\N	9d529084-5c4c-4f93-b083-5f0057d13390	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 22:42:56.973312+00
25	login_success	low	User successfully authenticated using password	1	\N	\N	3e18cfe3-9552-4516-bff3-e1d24bd91343	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 22:47:01.710361+00
26	login_success	low	User successfully authenticated using password	1	\N	\N	84c51723-66bf-413a-bd3b-8982ffe06682	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 23:03:22.539546+00
27	login_success	low	User successfully authenticated using password	1	\N	\N	5c43b396-a7a6-4b06-9a7a-0d190bae30a4	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 23:05:26.57999+00
28	login_success	low	User successfully authenticated using password	1	\N	\N	a0a1c4ce-7f15-4965-88ba-d0fe3e3adad0	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-24 23:18:41.58894+00
29	login_success	low	User successfully authenticated using password	1	\N	\N	436f38d7-99e1-4bc1-a358-0c0378152b36	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-25 01:41:33.449959+00
30	login_success	low	User successfully authenticated using password	1	\N	\N	adda1b4d-d760-4336-ad61-df8efc5ebfc8	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-25 03:02:55.952241+00
31	login_success	low	User successfully authenticated using password	1	\N	\N	1dd9b81b-ab4e-4ea3-ad7f-373c30fb52eb	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-25 07:53:13.003636+00
32	login_success	low	User successfully authenticated using password	1	\N	\N	20cf9a20-bbba-4fee-98f2-5736a33c82c4	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-25 08:29:42.630153+00
33	login_success	low	User successfully authenticated using password	1	\N	\N	2b588168-b0cc-421c-9475-8e62c1bd5271	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-25 08:35:50.169942+00
34	login_success	low	User successfully authenticated using password	1	\N	\N	907db25a-838a-4dc2-96c9-c8d24f5f23d2	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-25 10:23:00.888095+00
35	login_success	low	User successfully authenticated using password	1	\N	\N	b39ca3f0-48b4-4b82-a599-9e9fd69bac5c	\N	\N	172.19.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-25 22:54:36.303789+00
36	login_success	low	User successfully authenticated using password	1	\N	\N	105f0f71-c48b-425a-b669-8481fb0f9911	\N	\N	172.19.0.3	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-30 14:16:27.539471+00
37	login_success	low	User successfully authenticated using password	1	\N	\N	ac5bcb8d-9eb8-4171-8115-72e80e22b4cc	\N	\N	172.19.0.3	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-30 14:38:43.761353+00
38	login_success	low	User successfully authenticated using password	1	\N	\N	3c113808-337d-4d14-8907-0b280848e70a	\N	\N	172.19.0.3	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-30 14:54:25.444936+00
39	login_success	low	User successfully authenticated using password	1	\N	\N	63bea2b0-db71-461e-8891-563ba652eb2c	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 00:27:15.051067+00
40	login_success	low	User successfully authenticated using password	1	\N	\N	143c2743-2c4e-44b0-8ddb-e36580a34974	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 01:04:12.412466+00
41	login_success	low	User successfully authenticated using password	1	\N	\N	5502c0d2-120f-4364-89e9-0daaf1199783	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 01:49:18.048836+00
42	login_success	low	User successfully authenticated using password	1	\N	\N	c10806eb-9804-4c84-88af-af75d5ee5b88	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:05:26.786124+00
43	login_success	low	User successfully authenticated using password	1	\N	\N	a3dc6f61-eb3b-4402-aaac-1aed7a3d1543	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:19:14.968448+00
44	login_success	low	User successfully authenticated using password	1	\N	\N	852d9647-fec7-4018-ab21-092016844a41	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:31:39.501442+00
45	login_success	low	User successfully authenticated using password	1	\N	\N	7097fded-405e-487e-a129-1d0cd0f732ee	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:37:31.642251+00
46	login_success	low	User successfully authenticated using password	1	\N	\N	ef844f93-2ea6-4553-9e54-4ffd240e4feb	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:37:47.031922+00
47	login_success	low	User successfully authenticated using password	1	\N	\N	baa445e7-d41f-4406-af4b-b9532b059c50	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:40:07.099067+00
48	login_success	low	User successfully authenticated using password	1	\N	\N	43d47077-0cc8-4db2-9913-2ea0d15ac39f	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:46:28.524146+00
49	login_success	low	User successfully authenticated using password	1	\N	\N	e5ec6f0e-9741-4d3c-8a7c-172a593f8065	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 02:56:37.136179+00
50	login_success	low	User successfully authenticated using password	1	\N	\N	3f163bef-caf5-4b85-8b61-214c2cb72336	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 03:08:10.715596+00
51	login_success	low	User successfully authenticated using password	1	\N	\N	01e80094-c805-4fbf-87a3-a0631a86a3d7	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 03:57:39.591354+00
52	login_success	low	User successfully authenticated using password	1	\N	\N	b89e5866-6d15-49c9-8e9b-c48cec7477ab	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 04:14:24.385538+00
53	login_success	low	User successfully authenticated using password	1	\N	\N	dabe29c1-25c3-431b-968b-ba3c7d118515	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 04:16:05.232558+00
54	login_success	low	User successfully authenticated using password	1	\N	\N	e5875efc-71ab-457f-a80b-a7fffa273917	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 04:40:25.078725+00
55	login_success	low	User successfully authenticated using password	1	\N	\N	275f316d-971b-4c38-86f6-0346242bfcea	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 04:51:23.944445+00
56	login_success	low	User successfully authenticated using password	1	\N	\N	5497ef2c-60a0-416c-b7c8-b4b9740923ea	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 05:06:40.83912+00
57	login_success	low	User successfully authenticated using password	1	\N	\N	3c7b478b-9d29-4ee8-aa5b-63237ae0a95e	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 05:22:07.027631+00
58	login_success	low	User successfully authenticated using password	1	\N	\N	4d574644-0949-4d10-bc02-cb8a911684c1	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 05:32:08.279835+00
59	login_success	low	User successfully authenticated using password	1	\N	\N	0b9732a3-3a55-42ba-88ce-1b3ae377b384	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 05:42:06.10671+00
60	login_success	low	User successfully authenticated using password	1	\N	\N	91e5ab3b-5c9a-4e46-ba21-b2d128a70c70	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 05:59:23.659777+00
61	login_success	low	User successfully authenticated using password	1	\N	\N	bd1cdd6f-20e9-4c44-bf67-cdb5c8eef5a5	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 05:59:35.846489+00
62	login_success	low	User successfully authenticated using password	1	\N	\N	58c88c14-329b-47e1-82e8-5eb55174d0b2	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 06:13:57.912027+00
63	login_success	low	User successfully authenticated using password	1	\N	\N	06b081de-e44b-4a2a-a8e4-dc4c4bd65a07	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 06:15:02.19251+00
64	login_success	low	User successfully authenticated using password	1	\N	\N	98fc7398-4101-4b99-851f-acabae3ebd3f	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 06:37:31.590923+00
65	login_success	low	User successfully authenticated using password	1	\N	\N	a5df26c6-53fe-4ff6-8861-721a1f16b264	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:28:08.666102+00
66	login_success	low	User successfully authenticated using password	1	\N	\N	7dffd94c-1de9-417e-9fe1-b8c33f2956d4	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:30:30.301939+00
67	login_success	low	User successfully authenticated using password	1	\N	\N	0a50675c-6f5e-494d-9a4d-5f2ecd78a635	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:31:11.744685+00
68	login_success	low	User successfully authenticated using password	1	\N	\N	8c047565-ff13-4346-bb2e-98fd2e74c256	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:32:03.006074+00
69	login_success	low	User successfully authenticated using password	1	\N	\N	ff2188ac-a59e-442d-a47b-e039931edc6a	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:33:50.14965+00
70	login_success	low	User successfully authenticated using password	1	\N	\N	87761145-6df7-47ee-850c-dca1fb837d67	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:52:38.624426+00
71	login_success	low	User successfully authenticated using password	1	\N	\N	8378b02f-2fd1-4034-84f3-c1fef56ef6b2	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:56:13.552793+00
72	login_success	low	User successfully authenticated using password	1	\N	\N	71034104-ed9d-4a9d-93d6-994295559e3a	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 07:56:40.276223+00
73	login_success	low	User successfully authenticated using password	1	\N	\N	0630373c-582d-4d63-bc25-22e58ee7c7ee	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 08:05:12.934743+00
74	login_success	low	User successfully authenticated using password	1	\N	\N	1617150d-ab7b-46cf-b221-e14d04f6b3c9	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 08:14:29.426807+00
75	login_success	low	User successfully authenticated using password	1	\N	\N	8cc0044c-5b6c-4e05-a058-46c599c1b804	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 08:56:14.966548+00
76	login_success	low	User successfully authenticated using password	1	\N	\N	603f9fdf-a43e-438d-95e2-127b4acd1a52	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 08:58:33.382813+00
77	login_success	low	User successfully authenticated using password	1	\N	\N	698e7cb7-b691-4633-879d-b881cf1e565b	\N	\N	172.19.0.10	PostmanRuntime/7.45.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 08:58:44.760799+00
78	login_success	low	User successfully authenticated using password	1	\N	\N	a7ac0837-275b-4818-9507-fe6dc6bb4789	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 09:00:08.548955+00
79	login_success	low	User successfully authenticated using password	1	\N	\N	20a8c539-2a2d-4ec6-848c-812ef88764e0	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 09:02:38.399021+00
80	login_success	low	User successfully authenticated using password	1	\N	\N	e42e4673-1084-4d7e-93c5-b1d21b3ff0a2	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 09:25:04.22358+00
81	login_success	low	User successfully authenticated using password	1	\N	\N	85711cd9-1b3f-45da-a12a-5afe00d68d73	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 13:58:41.084641+00
82	login_success	low	User successfully authenticated using password	1	\N	\N	1886ecf3-4a1e-41b4-bbac-131c68e517e6	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 14:18:32.585052+00
83	login_success	low	User successfully authenticated using password	1	\N	\N	2feda893-c5bc-4143-a18c-886780e316a6	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 22:28:27.341401+00
84	login_success	low	User successfully authenticated using password	1	\N	\N	3ff09ca6-b452-40c9-bad5-c6f68b5d6beb	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 22:43:40.862312+00
85	login_success	low	User successfully authenticated using password	1	\N	\N	3780af84-eeb7-4cdb-8c0d-99b317a5bf18	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-08-31 23:03:35.746278+00
86	login_success	low	User successfully authenticated using password	1	\N	\N	52c451ad-2e6c-4ea9-9229-c6c5cf43cdfe	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 02:49:48.765156+00
87	login_success	low	User successfully authenticated using password	1	\N	\N	02796998-ecdb-424d-b8ed-2b7aa914249b	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 03:06:14.696504+00
88	login_success	low	User successfully authenticated using password	1	\N	\N	99881c33-0af5-48a4-beb7-01c0a1b8bd65	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 03:52:03.167203+00
89	login_success	low	User successfully authenticated using password	1	\N	\N	f2fbd1f4-2b31-4622-8ccc-7ae20afee222	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 04:11:21.715633+00
90	login_success	low	User successfully authenticated using password	1	\N	\N	1a009948-f4d4-4b6d-af67-ea34a898210f	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 05:37:09.374829+00
91	login_success	low	User successfully authenticated using password	1	\N	\N	80968547-a442-4cd5-9832-727ea8cc8bb6	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 06:16:56.964706+00
92	login_success	low	User successfully authenticated using password	1	\N	\N	c4a17eaf-61cd-4b8a-854c-877d88aa5056	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 06:54:06.093196+00
93	login_success	low	User successfully authenticated using password	1	\N	\N	076ec40f-3c37-4907-a138-c4e6eb7e0f16	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 08:18:38.944912+00
94	login_success	low	User successfully authenticated using password	1	\N	\N	cd822ff8-b68d-4ef0-9b4b-7237c5de5923	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 08:35:11.966751+00
95	login_success	low	User successfully authenticated using password	1	\N	\N	04ada2fa-6a41-4cfc-ad5c-44ad521fb610	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 09:05:24.675665+00
96	login_success	low	User successfully authenticated using password	1	\N	\N	b7c90a51-6220-4461-8a4e-b5dacbe46c62	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 09:06:09.945757+00
97	login_success	low	User successfully authenticated using password	1	\N	\N	3d824b08-cc7a-4652-9e6b-3e8eeff6745b	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 09:06:54.475588+00
98	login_success	low	User successfully authenticated using password	1	\N	\N	9d465491-56a6-4749-b8ee-6665f4d7e3d8	\N	\N	172.19.0.10	PostmanRuntime/7.45.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 09:18:55.822023+00
99	login_success	low	User successfully authenticated using password	1	\N	\N	5fbeff30-1b9c-471c-844b-0c981f285acf	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 09:28:58.868163+00
100	login_success	low	User successfully authenticated using password	1	\N	\N	5791a4df-8975-48aa-a509-5b70cc5d0554	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 09:46:20.36339+00
101	login_success	low	User successfully authenticated using password	1	\N	\N	51cb5e23-aa0b-4d56-92f3-f3a5047b838a	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 10:01:39.697074+00
102	login_success	low	User successfully authenticated using password	1	\N	\N	bf45974e-005a-404f-8a4c-bbe6614a8581	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 12:38:36.125725+00
103	login_success	low	User successfully authenticated using password	1	\N	\N	f2757cf7-2859-4a74-b660-39d841ad4623	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 12:54:14.867924+00
104	login_success	low	User successfully authenticated using password	1	\N	\N	f77cfb93-9b6d-47ee-b9be-eb50e894844e	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 13:49:31.061962+00
105	login_success	low	User successfully authenticated using password	1	\N	\N	f2232f4b-aaf2-4f3e-be53-0e6057d2f487	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-01 23:03:01.671507+00
106	login_success	low	User successfully authenticated using password	1	\N	\N	5054c8f4-dfbd-4f26-a82e-8ac76688a90d	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 00:59:50.213345+00
107	login_success	low	User successfully authenticated using password	1	\N	\N	3aa4e0d8-a829-467e-a0f4-2a0aff60f48f	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 01:39:31.334609+00
108	login_success	low	User successfully authenticated using password	1	\N	\N	6c4ff3c6-a7f6-43a2-9279-f8de9f92e343	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 01:56:13.539594+00
109	login_success	low	User successfully authenticated using password	1	\N	\N	84109a67-8bc1-4af6-8524-0c093dfc13e9	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 02:35:03.276428+00
110	login_success	low	User successfully authenticated using password	1	\N	\N	a3e6587f-3a3c-4f18-9447-181a005dc2cd	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 03:01:07.146261+00
111	login_success	low	User successfully authenticated using password	1	\N	\N	7660d697-8dda-4736-9252-b4471d5db353	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 03:23:29.538991+00
112	login_success	low	User successfully authenticated using password	1	\N	\N	6a17d0f4-fc17-4768-849d-b5d9c18a8753	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 05:23:25.401673+00
113	login_success	low	User successfully authenticated using password	1	\N	\N	d93140bf-9e6d-4d32-aef3-1d0b86f925b9	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 05:53:30.800633+00
114	login_success	low	User successfully authenticated using password	1	\N	\N	5aeefe93-c944-4f1e-bbd8-831474394f30	\N	\N	172.19.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 06:18:29.23615+00
115	login_success	low	User successfully authenticated using password	1	\N	\N	3d36ce5e-ad4b-4ec5-a483-be9fe8db5435	\N	\N	172.19.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 06:43:44.914485+00
116	login_success	low	User successfully authenticated using password	1	\N	\N	73b52f1f-4f70-4a37-b7b2-28892a348a60	\N	\N	172.19.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 07:08:01.171138+00
117	login_success	low	User successfully authenticated using password	1	\N	\N	52019a90-8eff-4902-bf88-71314dcd17aa	\N	\N	172.19.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 07:23:39.916254+00
118	login_success	low	User successfully authenticated using password	1	\N	\N	7ddb3978-0c01-4ab1-b191-00a22f0ce09f	\N	\N	172.19.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 07:44:00.584186+00
119	login_success	low	User successfully authenticated using password	1	\N	\N	7be7b0c1-c966-406c-baa9-4a8f803e768f	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 08:00:51.15348+00
120	login_success	low	User successfully authenticated using password	1	\N	\N	b4454e46-78f7-480b-b258-c62fc175a895	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 09:19:42.504229+00
121	login_success	low	User successfully authenticated using password	1	\N	\N	e7317db8-d0f7-4646-851e-fc6d4f4b0ed3	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 09:25:24.108023+00
122	login_success	low	User successfully authenticated using password	1	\N	\N	315f3c8d-94e6-440b-a9fc-6d2401eae4ad	\N	\N	172.19.0.1	curl/7.81.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 09:25:45.333277+00
123	login_success	low	User successfully authenticated using password	1	\N	\N	52af72c1-c399-46b8-a391-71df96137f10	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 09:50:18.715684+00
124	login_success	low	User successfully authenticated using password	1	\N	\N	165fe6ed-e670-47b5-9507-b59d35798d45	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 13:41:46.426489+00
125	login_success	low	User successfully authenticated using password	1	\N	\N	1c35e822-09c9-405a-bfdc-3f78917a9e0b	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 14:23:53.125698+00
126	login_success	low	User successfully authenticated using password	1	\N	\N	2a24800d-4f85-4561-98e0-a2be16a3f3c0	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 21:37:14.482388+00
127	login_success	low	User successfully authenticated using password	1	\N	\N	821bb711-4712-4657-8ec7-d97891196431	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 22:43:02.589116+00
128	login_success	low	User successfully authenticated using password	1	\N	\N	1f7dd4cd-cf51-46ed-8a75-c4c41fb21318	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-02 22:59:18.042254+00
129	login_success	low	User successfully authenticated using password	1	\N	\N	ef2c858f-397c-49a6-97cd-4ae33ae6dd4c	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 01:35:53.308547+00
130	login_success	low	User successfully authenticated using password	1	\N	\N	92b093d1-ae89-4e45-a886-1501c7b761fb	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 03:52:59.795+00
131	login_success	low	User successfully authenticated using password	1	\N	\N	0bffafd0-e921-4e3c-86de-9bd78811d7b4	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 04:13:12.959898+00
132	login_success	low	User successfully authenticated using password	1	\N	\N	bf6d47c9-84b4-462c-89d3-8a98d712afc2	\N	\N	172.19.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 04:33:05.781408+00
133	login_success	low	User successfully authenticated using password	1	\N	\N	9230fe4f-0e8e-4951-9b3f-e65e59e45b33	\N	\N	172.19.0.9	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 05:03:56.839059+00
134	login_success	low	User successfully authenticated using password	1	\N	\N	77cecf36-b355-4d90-908d-e79e9a48afa0	\N	\N	172.19.0.9	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 06:03:55.821319+00
135	login_success	low	User successfully authenticated using password	1	\N	\N	c1b614d3-9045-4e77-b22c-95b9e7edc15d	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 08:09:17.623155+00
136	login_success	low	User successfully authenticated using password	1	\N	\N	1ffaeecc-548e-4479-a4fd-61e26235fac2	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-03 09:39:16.59656+00
137	login_success	low	User successfully authenticated using password	1	\N	\N	a9ff5682-d381-4d75-bbd6-5534394e820e	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 04:04:23.175928+00
138	login_success	low	User successfully authenticated using password	1	\N	\N	f0f5e4c8-2f2d-4d40-9837-34f7d029657e	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 07:53:44.896829+00
139	login_success	low	User successfully authenticated using password	1	\N	\N	449ed0e2-f069-4160-87e6-8b9102246bd8	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 08:10:35.919999+00
140	login_success	low	User successfully authenticated using password	1	\N	\N	03f09f22-a0d9-4026-9dfd-5bbeefb722b0	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 08:13:17.753016+00
141	login_success	low	User successfully authenticated using password	1	\N	\N	9bc47fdf-d14d-4c55-9dd2-04b5c3326cd5	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 08:35:26.520857+00
142	login_success	low	User successfully authenticated using password	1	\N	\N	d5311812-80b3-4b8c-af60-841c070b8090	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 09:51:28.834299+00
143	login_success	low	User successfully authenticated using password	1	\N	\N	b00a91f5-8e85-463b-84c3-7a4868587c7f	\N	\N	172.19.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 21:38:14.198952+00
144	login_success	low	User successfully authenticated using password	1	\N	\N	9f63751a-a904-400a-b1d7-5231543dd583	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-04 23:13:12.944861+00
145	login_success	low	User successfully authenticated using password	1	\N	\N	722d4c76-375f-4620-bdc8-2b35a399f5c2	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-05 00:15:59.376187+00
146	login_success	low	User successfully authenticated using password	1	\N	\N	5d61031d-15a0-4124-a7a2-fadac429931d	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-07 13:01:35.72873+00
147	login_success	low	User successfully authenticated using password	1	\N	\N	593705b1-22b3-4d12-b4a5-27fe15f495c8	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-07 13:01:54.73815+00
148	login_success	low	User successfully authenticated using password	1	\N	\N	f78825a7-4880-4fec-8f67-2e3e346046e4	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-07 22:59:33.678171+00
149	login_success	low	User successfully authenticated using password	1	\N	\N	9e77912e-4af7-43c4-a428-d4eb50eeb781	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 05:05:27.077107+00
150	login_success	low	User successfully authenticated using password	1	\N	\N	ccb53b1f-b9b9-4d0e-9e4b-cf702bfbe681	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 05:52:51.828389+00
151	login_success	low	User successfully authenticated using password	1	\N	\N	b63457a8-0b28-4845-9beb-e72e6824b779	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 07:23:03.693579+00
152	login_success	low	User successfully authenticated using password	1	\N	\N	047b348c-15d9-425b-82d5-1256b4fae973	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 08:41:26.501265+00
153	login_success	low	User successfully authenticated using password	1	\N	\N	37ea4e58-35ee-44dd-967b-6ada9a02292b	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 08:57:28.257859+00
154	login_success	low	User successfully authenticated using password	1	\N	\N	8194d64c-f02f-44dd-b264-60eb5318d65c	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 10:14:49.981731+00
155	login_success	low	User successfully authenticated using password	1	\N	\N	07139aea-1b82-4b1f-84c5-affcf42cb040	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 21:39:41.564927+00
156	login_success	low	User successfully authenticated using password	1	\N	\N	cfa2632a-2f24-4d62-aa4e-3ad95ab6d892	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 22:13:05.00729+00
157	login_success	low	User successfully authenticated using password	1	\N	\N	e0081aa9-4cfb-431c-b4c2-05707d518685	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 22:30:13.338445+00
158	login_success	low	User successfully authenticated using password	1	\N	\N	e53a6134-f1b7-4982-891e-89aa5a1cc9e8	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-10 22:45:15.204902+00
159	login_success	low	User successfully authenticated using password	1	\N	\N	43f5cf6a-b4b6-411a-befc-a2650d715e56	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 02:18:00.313557+00
160	login_success	low	User successfully authenticated using password	1	\N	\N	709bec52-aff9-4ab1-bd77-fd4135b2a4a2	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 03:46:51.916637+00
161	login_success	low	User successfully authenticated using password	1	\N	\N	36572d59-251c-4f51-9f36-242666c84ad1	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 04:20:03.977345+00
162	login_success	low	User successfully authenticated using password	1	\N	\N	cdb61ccd-436e-494c-ab46-3e753ac40097	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 04:38:24.217415+00
163	login_success	low	User successfully authenticated using password	1	\N	\N	b15a11b0-3c99-4be9-94b6-f55059c44159	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 06:53:35.494117+00
164	login_success	low	User successfully authenticated using password	1	\N	\N	b690a140-888c-4439-adfa-a40231e5e639	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 07:09:47.188816+00
165	login_success	low	User successfully authenticated using password	1	\N	\N	76f63d92-ad56-4cf5-8d95-b035a155fd50	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 07:25:09.797046+00
166	login_success	low	User successfully authenticated using password	1	\N	\N	f28239ab-be5a-474d-b6bb-13f12c865b73	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 07:59:38.390111+00
167	login_success	low	User successfully authenticated using password	1	\N	\N	e1d0c030-a87c-4362-a332-c60259935099	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 10:29:38.96595+00
168	login_success	low	User successfully authenticated using password	1	\N	\N	b36ff361-91f9-4611-b739-c60d5dd7a4aa	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-11 10:52:49.532817+00
169	login_success	low	User successfully authenticated using password	1	\N	\N	e31b1a0d-d364-4165-b611-1978c85e9b51	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 00:14:51.200748+00
170	login_success	low	User successfully authenticated using password	1	\N	\N	15015c11-aa18-4351-b831-00c6c56bdfe4	\N	\N	172.23.0.18	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 00:42:00.592108+00
171	login_success	low	User successfully authenticated using password	1	\N	\N	af77a0af-4335-46cf-adca-ad9a23b97743	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 02:10:28.704084+00
172	login_success	low	User successfully authenticated using password	1	\N	\N	83f794dd-0963-4867-ad04-39e3e8b9d797	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 22:13:58.259822+00
173	login_success	low	User successfully authenticated using password	1	\N	\N	33d29474-37e5-4e6e-a421-850c17b4b736	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 22:29:48.474908+00
174	login_success	low	User successfully authenticated using password	1	\N	\N	94457fbe-d464-4bfe-8781-1ca1971b57e6	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 22:47:02.329713+00
175	login_success	low	User successfully authenticated using password	1	\N	\N	1732b4a1-287d-476e-9520-9db8eb08c5f7	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 23:09:01.915009+00
176	login_success	low	User successfully authenticated using password	1	\N	\N	51ed6424-05f0-40d4-8bc8-a53210021397	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-12 23:24:03.581171+00
177	login_success	low	User successfully authenticated using password	1	\N	\N	70936bc9-af88-425c-a2bd-6b10bcc20ac8	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 02:37:04.377373+00
178	login_success	low	User successfully authenticated using password	1	\N	\N	b115a66e-0951-4487-94f8-6a729722ef79	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 02:52:22.942132+00
179	login_success	low	User successfully authenticated using password	1	\N	\N	feac3d27-5d4e-4ae7-9b0d-75588479b11e	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 03:07:40.576151+00
180	login_success	low	User successfully authenticated using password	1	\N	\N	c63439cf-7f6f-438f-a83b-c5ea9039bd92	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 04:12:25.144582+00
181	login_success	low	User successfully authenticated using password	1	\N	\N	6ccc143a-20bb-4d30-9e67-7b35b2d92257	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 04:32:50.388904+00
182	login_success	low	User successfully authenticated using password	1	\N	\N	c5d0e714-aaf8-4785-af0e-2be9c3f601f3	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 04:47:59.878459+00
183	login_success	low	User successfully authenticated using password	1	\N	\N	be5857c9-1dfc-4644-b325-5bfcb117ce85	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 05:06:00.766079+00
184	login_success	low	User successfully authenticated using password	1	\N	\N	bacdb6be-5c12-4495-86ac-edb778f908e7	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 08:49:01.547979+00
185	login_success	low	User successfully authenticated using password	1	\N	\N	84a1b898-c9da-4f46-8654-1f726c07758b	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 09:05:15.651531+00
186	login_success	low	User successfully authenticated using password	1	\N	\N	3c832907-d7e8-4a2a-a28d-3772eb1a8dd9	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 09:28:38.149697+00
187	login_success	low	User successfully authenticated using password	1	\N	\N	7bd488cb-fb23-4b03-8b9a-4f49df6d4eef	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 10:02:58.062057+00
188	login_success	low	User successfully authenticated using password	1	\N	\N	a8d3ecd3-6595-4676-b2aa-dc55c0ca4a81	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 22:12:58.084036+00
189	login_success	low	User successfully authenticated using password	1	\N	\N	c0246e09-4ab2-43a8-9081-2ab02e04988f	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 22:30:59.203769+00
190	login_success	low	User successfully authenticated using password	1	\N	\N	ce2a696c-8010-4a50-8f94-fe50f434b8e0	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 22:53:41.324767+00
191	login_success	low	User successfully authenticated using password	1	\N	\N	a2c9d48b-a412-4246-b730-c131bb9c130f	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 23:09:43.758731+00
192	login_success	low	User successfully authenticated using password	1	\N	\N	1063f60a-9f84-438e-81ce-bc3e37d00642	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 23:26:05.896286+00
193	login_success	low	User successfully authenticated using password	1	\N	\N	fd61ec13-4128-4f47-8119-a3ac5021de4b	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-13 23:41:09.075363+00
194	login_success	low	User successfully authenticated using password	1	\N	\N	68108db2-e1e2-4836-b6df-5f8095c74cd9	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 12:32:32.055396+00
195	login_success	low	User successfully authenticated using password	1	\N	\N	6e41e167-e754-49e0-8fc6-96b38a6b5f86	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 12:34:00.870527+00
196	login_success	low	User successfully authenticated using password	1	\N	\N	6e8ead08-ff3c-4b9c-b1bf-75f2352a0cd3	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 12:35:43.654018+00
197	login_success	low	User successfully authenticated using password	1	\N	\N	770e8af0-2b97-49f8-8f0b-d4a98a631913	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 12:37:47.673876+00
198	login_success	low	User successfully authenticated using password	1	\N	\N	298cad27-afdb-49e8-bc6c-982573af7a2c	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 12:54:07.758141+00
199	login_success	low	User successfully authenticated using password	1	\N	\N	6230c60c-a24d-4393-8cab-c8e29caa6396	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 13:09:45.219899+00
200	login_success	low	User successfully authenticated using password	1	\N	\N	3bd81cb0-bca7-4c9b-8a76-18e417b5b3c3	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 13:24:54.704375+00
201	login_success	low	User successfully authenticated using password	1	\N	\N	cc15d169-0271-4655-a95e-a15d47177a91	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 21:21:27.673938+00
202	login_success	low	User successfully authenticated using password	1	\N	\N	1b314942-2a2d-49d0-88cb-6faaf94e1961	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 21:37:01.149066+00
203	login_success	low	User successfully authenticated using password	1	\N	\N	d4e7f7d3-ea2e-4c2d-9ece-0a577c4cd60c	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 22:17:38.804839+00
204	login_success	low	User successfully authenticated using password	1	\N	\N	a810ff87-50d3-4f1a-b303-8f94f356e742	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 22:34:07.34784+00
205	login_success	low	User successfully authenticated using password	1	\N	\N	bc89557d-9570-4d40-94e3-c9a639f83c72	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-14 22:53:16.19229+00
206	login_success	low	User successfully authenticated using password	1	\N	\N	2375b535-c825-4f94-be63-e757f63a63ab	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 02:25:47.459186+00
207	login_success	low	User successfully authenticated using password	1	\N	\N	171e21de-c0c0-4684-9cb5-3d1b0a68f5dd	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 02:41:25.535202+00
208	login_success	low	User successfully authenticated using password	1	\N	\N	53c558fe-6a07-40f0-87bc-c5217fb039de	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 03:09:40.152717+00
209	login_success	low	User successfully authenticated using password	1	\N	\N	b8733aea-c1ef-4df0-8642-67826ec5cb21	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 04:20:10.274242+00
210	login_success	low	User successfully authenticated using password	1	\N	\N	4be7e85e-bf41-41bb-af24-ac6bd72a033d	\N	\N	172.23.0.8	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 04:38:14.152116+00
211	login_success	low	User successfully authenticated using password	1	\N	\N	90d15260-e227-4dfd-a7a4-703d8f5e3487	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 07:44:26.054371+00
212	login_success	low	User successfully authenticated using password	1	\N	\N	fa02dd1a-deb8-457b-8d55-907f2d116868	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 08:03:23.64993+00
213	login_success	low	User successfully authenticated using password	1	\N	\N	55a08f2a-d4c9-4a4f-bb2f-556682e43270	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 08:19:08.710379+00
214	login_success	low	User successfully authenticated using password	1	\N	\N	95717a18-7ab7-4846-8453-65dba04eada1	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 08:47:55.835689+00
215	login_success	low	User successfully authenticated using password	1	\N	\N	5ac2152d-5f58-40d5-a0a4-45fcfa98db4b	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 09:04:32.717448+00
216	login_success	low	User successfully authenticated using password	1	\N	\N	d67811c8-5ffe-483e-805f-3540940cd077	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 09:20:23.803252+00
217	login_success	low	User successfully authenticated using password	1	\N	\N	7b7ba96c-ce19-4026-a995-e835f93619f0	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 09:39:37.180386+00
218	login_success	low	User successfully authenticated using password	1	\N	\N	49014819-b97c-4b52-bfa0-12e769b54a90	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 10:03:14.813408+00
219	login_success	low	User successfully authenticated using password	1	\N	\N	92bf4dd6-8fd1-4c9d-8816-f7024ff82eb2	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 10:21:00.45635+00
220	login_success	low	User successfully authenticated using password	1	\N	\N	6100d94f-d7ce-4371-bf49-570258eae61c	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 13:00:42.396672+00
221	login_success	low	User successfully authenticated using password	1	\N	\N	d782c88d-f734-49f5-9c94-41740b1fc4d3	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 21:20:30.840285+00
222	login_success	low	User successfully authenticated using password	1	\N	\N	4ea60b7b-9fca-4e16-9618-019b5400ae4d	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 21:36:51.792942+00
223	login_success	low	User successfully authenticated using password	1	\N	\N	70635278-275f-4142-802c-b261c8ef37d4	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 21:42:38.06748+00
224	login_success	low	User successfully authenticated using password	1	\N	\N	1dee00d9-bf09-41ef-a08c-c117417b34da	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 22:21:40.702568+00
225	login_success	low	User successfully authenticated using password	1	\N	\N	cbdaf27f-f048-4ee3-9932-b58fc3eaf5d6	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-15 22:42:33.080904+00
226	login_success	low	User successfully authenticated using password	1	\N	\N	f9052938-575d-4659-9fc0-821499b6c513	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-16 03:24:12.687462+00
227	login_success	low	User successfully authenticated using password	1	\N	\N	3151b041-30ce-41fc-8ade-b8ef50c2a47b	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-16 05:16:23.974956+00
228	login_success	low	User successfully authenticated using password	1	\N	\N	54c02a1c-a76c-42f6-87f3-bd5618cd157c	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 01:39:59.778798+00
229	login_success	low	User successfully authenticated using password	1	\N	\N	4a3a975c-3d1e-4241-a538-3d7eb560a368	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 03:03:20.174539+00
230	login_success	low	User successfully authenticated using password	1	\N	\N	2ddc20b1-d5cd-4bd1-b0ad-5fcd47b4bac0	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 07:50:04.435334+00
231	login_success	low	User successfully authenticated using password	1	\N	\N	e59776d2-0dff-4928-a1e0-5242fd560bee	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 08:54:17.379607+00
232	login_success	low	User successfully authenticated using password	1	\N	\N	88f8ee3a-3b69-4200-bb88-5524bae20cff	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 09:03:17.810833+00
233	login_success	low	User successfully authenticated using password	1	\N	\N	364b83ee-eb5e-4fdb-a28c-af04a86a29d2	\N	\N	172.23.0.16	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 09:54:14.980208+00
234	login_success	low	User successfully authenticated using password	1	\N	\N	e330e0cb-52d7-48f8-9fbe-7ea8f9a30ef1	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 12:35:14.059378+00
235	login_success	low	User successfully authenticated using password	1	\N	\N	111917ae-32eb-4cae-9e96-c8f5c373180d	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 12:51:00.004429+00
236	login_success	low	User successfully authenticated using password	1	\N	\N	a28f5cdc-6a82-4b68-bdce-6e3b372b973e	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 13:09:34.895488+00
237	login_success	low	User successfully authenticated using password	1	\N	\N	7d6bbd30-6f10-4ca9-a2a9-d7ddf2953e0e	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 22:30:00.826309+00
238	login_success	low	User successfully authenticated using password	1	\N	\N	d267dbeb-f70e-466a-b6ea-589e8622a0eb	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-17 22:47:25.943738+00
239	login_success	low	User successfully authenticated using password	1	\N	\N	3ae8a43b-e4f0-4aba-82bb-8a207200fe81	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 02:26:27.141372+00
240	login_success	low	User successfully authenticated using password	1	\N	\N	5a5b5522-5265-4e01-a73c-8da1880528ce	\N	\N	172.23.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 03:20:39.031461+00
241	login_success	low	User successfully authenticated using password	1	\N	\N	0d534e50-7837-451d-b55b-ba7d71f74c48	\N	\N	172.23.0.13	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 03:43:17.41206+00
242	login_success	low	User successfully authenticated using password	1	\N	\N	f698895a-5441-47f7-af1f-3b732cc8b961	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 05:03:50.909494+00
243	login_success	low	User successfully authenticated using password	1	\N	\N	ded60bc2-4eef-43ce-be10-cded53f4faac	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 05:36:15.699962+00
244	login_success	low	User successfully authenticated using password	1	\N	\N	885cdcc5-8915-42e6-9f8c-d95b51101db9	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 05:54:22.770669+00
245	login_success	low	User successfully authenticated using password	1	\N	\N	35d29369-7018-4376-826f-fc4e27aaaa74	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 09:29:55.556937+00
246	login_success	low	User successfully authenticated using password	1	\N	\N	1ec0bc8a-7b16-495f-8685-c831038b1b31	\N	\N	172.23.0.9	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 09:48:03.078948+00
247	login_success	low	User successfully authenticated using password	1	\N	\N	d2d9bce0-6067-4d45-bfa0-9533e0810a0a	\N	\N	172.23.0.9	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 10:04:37.970182+00
248	login_success	low	User successfully authenticated using password	1	\N	\N	557195a0-77de-4033-8604-8b65a9002712	\N	\N	172.23.0.9	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 10:21:46.227615+00
249	login_success	low	User successfully authenticated using password	1	\N	\N	fecbd45c-67b3-479d-807e-be68ca968bee	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 12:51:39.511814+00
250	login_success	low	User successfully authenticated using password	1	\N	\N	972440be-b48c-4f71-b694-024815d59ee7	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 13:08:26.017006+00
251	login_success	low	User successfully authenticated using password	1	\N	\N	72b4f364-6eee-4ba3-a292-d5972945a448	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 13:24:39.622182+00
252	login_success	low	User successfully authenticated using password	1	\N	\N	a2449724-c3df-4f37-aea6-64e21a0de4f2	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 22:14:46.990812+00
253	login_success	low	User successfully authenticated using password	1	\N	\N	f60c756f-ce87-487a-8e99-708bce9142c7	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 22:44:13.6791+00
254	login_success	low	User successfully authenticated using password	1	\N	\N	e1d90426-dae2-4f8e-9341-6779d8a583d6	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 22:45:48.478608+00
255	login_success	low	User successfully authenticated using password	1	\N	\N	bf0af90b-1978-4495-b10a-529788f84451	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 22:51:48.692073+00
256	login_success	low	User successfully authenticated using password	1	\N	\N	879559b4-bc2b-4a3d-91fc-cfbb89480620	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-18 23:00:42.949702+00
257	login_success	low	User successfully authenticated using password	1	\N	\N	fda06999-bd7f-4f06-8ef3-49290f39adf3	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 02:13:30.50845+00
258	login_success	low	User successfully authenticated using password	1	\N	\N	d30c0425-98fb-46b1-ba10-39388cc56341	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 02:51:49.413559+00
259	login_success	low	User successfully authenticated using password	1	\N	\N	6123a4e8-b351-487d-896a-ed9cfbb64dbe	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 03:12:36.582449+00
260	login_success	low	User successfully authenticated using password	1	\N	\N	7dc3072f-223c-4db6-893a-e6975f5eb1a2	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 03:32:14.852041+00
261	login_success	low	User successfully authenticated using password	1	\N	\N	7047fa67-2599-499f-bd5e-5160961e9995	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 03:48:55.683399+00
262	login_success	low	User successfully authenticated using password	1	\N	\N	d7ab3856-5592-487f-a2fb-85d389facfb6	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 04:10:47.377502+00
263	login_success	low	User successfully authenticated using password	1	\N	\N	addcf7f9-5872-4c06-b367-63fee212d79e	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 04:31:10.116172+00
264	login_success	low	User successfully authenticated using password	1	\N	\N	8b492750-ae76-47c1-9c3b-3fbb4c5acc59	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 05:22:49.952704+00
265	login_success	low	User successfully authenticated using password	1	\N	\N	55f27465-886e-4375-8701-807b8d01cf99	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 05:46:42.387179+00
266	login_success	low	User successfully authenticated using password	1	\N	\N	be6d2108-d6e8-4f82-a1c7-cde300dceb2c	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 06:05:39.632982+00
267	login_success	low	User successfully authenticated using password	1	\N	\N	d13583d7-b8dd-4886-8631-0c4dbae9f55d	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 06:22:51.710344+00
268	login_success	low	User successfully authenticated using password	1	\N	\N	ad6c850f-d30f-4274-8d8a-ce1824cbfe2f	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 09:22:47.917986+00
269	login_success	low	User successfully authenticated using password	1	\N	\N	38d3816a-3cc2-4d95-b4ef-2194dbdbec08	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 09:42:40.697326+00
270	login_success	low	User successfully authenticated using password	1	\N	\N	e511238e-cac6-49e2-b943-3977c4fba32c	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 21:28:46.026284+00
271	login_success	low	User successfully authenticated using password	1	\N	\N	95722c49-05ce-4194-9a1a-40c3fc0db710	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 22:14:36.831956+00
272	login_success	low	User successfully authenticated using password	1	\N	\N	d3e7a5da-41cd-45c8-aa1a-1271215d3a77	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 22:40:46.224321+00
273	login_success	low	User successfully authenticated using password	1	\N	\N	ce4c1752-a33c-4e85-97e4-6db010b203f4	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-19 22:56:38.236641+00
274	login_success	low	User successfully authenticated using password	1	\N	\N	642a8b7b-bddb-486b-8d7a-d8ee7e6f5157	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-20 08:39:24.990712+00
275	login_success	low	User successfully authenticated using password	1	\N	\N	11dcd124-cb40-41d1-93a2-c3ab0a0222f7	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-20 12:28:51.028847+00
276	login_success	low	User successfully authenticated using password	1	\N	\N	4707aefa-e28d-4aa7-8a62-16ed58095377	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 06:18:51.643196+00
277	login_success	low	User successfully authenticated using password	1	\N	\N	882005da-0bc1-41bc-9fff-31c8f4700fba	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 06:53:30.359242+00
278	login_success	low	User successfully authenticated using password	1	\N	\N	73fca07f-a1a2-44ec-8c59-143334cd1113	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 09:32:39.230969+00
279	login_success	low	User successfully authenticated using password	1	\N	\N	6ccf793d-3099-4a83-9689-31428fd0da67	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 10:02:15.729556+00
280	login_success	low	User successfully authenticated using password	1	\N	\N	e62aa5a5-9a92-4a66-a031-7f03bab8228a	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 10:26:02.055679+00
281	login_success	low	User successfully authenticated using password	1	\N	\N	34f746e1-b447-45b4-9223-182a28ffddec	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 22:17:26.793713+00
282	login_success	low	User successfully authenticated using password	1	\N	\N	1db096be-0c47-4173-a03a-125a3cfecc9e	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 22:40:02.014465+00
283	login_success	low	User successfully authenticated using password	1	\N	\N	f303bf0f-4b80-45d0-84cf-ff119655b4b2	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-25 22:56:04.719048+00
284	login_success	low	User successfully authenticated using password	1	\N	\N	f17c28e8-8489-481a-9f0d-1248d9e5a0ca	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 04:11:36.260854+00
285	login_success	low	User successfully authenticated using password	1	\N	\N	7262095f-10f9-4c51-a53f-d6176c495cb1	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 06:53:38.069464+00
286	login_success	low	User successfully authenticated using password	1	\N	\N	44d54cb0-f220-4c43-b68a-538a39809aee	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 06:54:04.898265+00
287	login_success	low	User successfully authenticated using password	1	\N	\N	d18a6fac-44a9-48fd-bcef-7d939cf5828b	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 07:20:19.309507+00
288	login_success	low	User successfully authenticated using password	1	\N	\N	37ac5fa0-a1f2-4ec6-bc2a-56608fb0d025	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 07:21:12.070057+00
289	login_success	low	User successfully authenticated using password	1	\N	\N	fe14d9cf-19b9-48e7-93e8-6fab6d937332	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 09:36:18.170045+00
290	login_success	low	User successfully authenticated using password	1	\N	\N	4847e268-830b-4f07-81c7-266eab9aab7e	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 09:50:05.916988+00
291	login_success	low	User successfully authenticated using password	1	\N	\N	3a5f0aac-9555-4879-8713-5efe34c7c949	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 10:04:10.332713+00
292	login_success	low	User successfully authenticated using password	1	\N	\N	14309a71-ee15-49c1-acca-25f0b2bc996b	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-26 10:33:40.287943+00
293	login_success	low	User successfully authenticated using password	1	\N	\N	6b27a99f-2ae6-4361-92b9-1f0bb1823fec	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-27 23:51:47.282139+00
294	login_success	low	User successfully authenticated using password	1	\N	\N	e874d9c1-3410-4779-bf5f-112b931749f5	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-28 13:08:20.774577+00
295	login_success	low	User successfully authenticated using password	1	\N	\N	7d8c998c-11f3-450f-a1da-4f3ae4e85536	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 04:18:10.964963+00
296	login_success	low	User successfully authenticated using password	1	\N	\N	abbc742f-03fa-4084-8564-7f85007b961e	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 04:34:31.373529+00
297	login_success	low	User successfully authenticated using password	1	\N	\N	6b296871-a5a9-4705-acb6-3ef920b5511c	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 05:22:24.138639+00
298	login_success	low	User successfully authenticated using password	1	\N	\N	af331d77-fdb6-4c00-82e4-32d20be11f26	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 08:21:42.924997+00
299	login_success	low	User successfully authenticated using password	1	\N	\N	769a0121-5bb0-431b-82cd-f67c57a8effb	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 08:57:57.098278+00
300	login_success	low	User successfully authenticated using password	1	\N	\N	b670e90e-cdfb-4b32-8a54-b9c60c94c4c3	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 10:10:25.787262+00
301	login_success	low	User successfully authenticated using password	1	\N	\N	f7c16868-53e9-4ba1-af06-16719682077e	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 10:26:10.969612+00
302	login_success	low	User successfully authenticated using password	1	\N	\N	c9270d4c-77e6-4569-aaae-d46e03b5d809	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 10:52:24.345165+00
303	login_success	low	User successfully authenticated using password	1	\N	\N	011a02de-a5aa-480d-b06c-68a6ccfba35d	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 11:34:24.552963+00
304	login_success	low	User successfully authenticated using password	1	\N	\N	7808df23-4c27-49d4-8bc3-ef42ea250b91	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-09-30 22:21:54.850701+00
305	login_success	low	User successfully authenticated using password	1	\N	\N	57b9ab20-7299-421c-a4e9-8b3c4ac9df71	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 03:18:50.461465+00
306	login_success	low	User successfully authenticated using password	1	\N	\N	8c157105-53d9-487e-a792-c08f6112935b	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 06:03:37.685929+00
307	login_success	low	User successfully authenticated using password	1	\N	\N	fc223f10-7520-4547-9382-252f017326f0	\N	\N	172.23.0.11	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 06:57:46.212872+00
308	login_success	low	User successfully authenticated using password	1	\N	\N	bc586b30-ac6d-4eb4-9b62-2b187853deb0	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 08:44:22.283304+00
309	login_success	low	User successfully authenticated using password	1	\N	\N	c0bf0554-20ea-4536-8442-a63931a2153b	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 10:15:35.995072+00
310	login_success	low	User successfully authenticated using password	1	\N	\N	c6d60266-18cb-443d-8069-159b990694f9	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 10:32:00.663888+00
311	login_success	low	User successfully authenticated using password	1	\N	\N	97560edd-4430-4b20-9f71-1377b749a820	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 10:47:55.688937+00
312	login_success	low	User successfully authenticated using password	1	\N	\N	a6fa2da6-b09f-40a1-896d-27ab7fdc61d2	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 20:55:16.929089+00
313	login_success	low	User successfully authenticated using password	1	\N	\N	f88cdb08-a9a5-4350-bc76-40d8c5fc2ac2	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 21:10:59.41449+00
314	login_success	low	User successfully authenticated using password	1	\N	\N	f594d134-228f-4f89-9a5e-234a27eb6b26	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 22:06:25.441957+00
315	login_success	low	User successfully authenticated using password	1	\N	\N	f9ed517c-ca1e-4412-993b-ff2c976e8cd4	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-01 22:22:18.498+00
316	login_success	low	User successfully authenticated using password	1	\N	\N	d75fbdd0-cf08-40d3-af8d-a53d6e14afd9	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-02 05:44:23.308332+00
317	login_success	low	User successfully authenticated using password	1	\N	\N	9b38ccb9-579f-4ae0-aecc-f215d9e86a02	\N	\N	172.23.0.19	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-02 06:01:28.196959+00
318	login_success	low	User successfully authenticated using password	1	\N	\N	9c16b516-c57b-4f51-809f-9ba37b74fd01	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-02 06:19:31.162775+00
319	login_success	low	User successfully authenticated using password	1	\N	\N	ced89257-5944-4bff-b5e2-72709b7ee218	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-02 06:35:36.752606+00
320	login_success	low	User successfully authenticated using password	1	\N	\N	5d0f0834-3969-4b4c-80e0-ea056bfab86e	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-02 07:02:38.769526+00
321	login_success	low	User successfully authenticated using password	1	\N	\N	316b1c0f-d73b-4aca-9249-f00b6bf80b74	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-02 07:21:18.797549+00
322	login_success	low	User successfully authenticated using password	1	\N	\N	6cd2f9b4-72ec-439c-bc9a-4b1bc30b4fee	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-07 10:00:43.367693+00
323	login_success	low	User successfully authenticated using password	1	\N	\N	ca562e0e-889d-4d4a-b35a-4a9e80e03dac	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-07 10:19:10.368236+00
324	login_success	low	User successfully authenticated using password	1	\N	\N	805f509c-0ea8-4309-8790-62a3666771e6	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-07 10:46:56.525852+00
325	login_success	low	User successfully authenticated using password	1	\N	\N	8fd6ee01-846a-4748-a7fc-8dfcffb9b4f7	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-07 22:24:39.021598+00
326	login_success	low	User successfully authenticated using password	1	\N	\N	9e135b6f-a1ec-4502-a5e3-f14d4863c602	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 07:26:37.268351+00
327	login_success	low	User successfully authenticated using password	1	\N	\N	95b5d998-2356-4bc1-a43b-ebf0ec1ad2c3	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 07:51:03.085773+00
328	login_success	low	User successfully authenticated using password	1	\N	\N	1cccbb5a-e636-496d-8496-37526f2d8fd9	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 09:20:31.903691+00
329	login_success	low	User successfully authenticated using password	1	\N	\N	986ce01b-80b0-4a21-aa78-6c038551a6c5	\N	\N	172.23.0.15	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 09:45:31.284643+00
330	login_success	low	User successfully authenticated using password	1	\N	\N	27d86063-0669-4362-a451-ef077ac95ea7	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 10:01:36.504283+00
331	login_success	low	User successfully authenticated using password	1	\N	\N	852d06dd-ba83-40f5-a649-b5a80bcfba87	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 10:22:11.328984+00
332	login_success	low	User successfully authenticated using password	1	\N	\N	93452be7-854d-4a99-9049-12120b7ccd07	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 22:18:11.984874+00
333	login_success	low	User successfully authenticated using password	1	\N	\N	e2b6dd6b-d258-43d6-a8ef-d5b1f094b1ea	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 22:33:15.481957+00
334	login_success	low	User successfully authenticated using password	1	\N	\N	32519832-b88e-48ae-b34b-e6d921e71d25	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 22:54:30.78819+00
335	login_success	low	User successfully authenticated using password	1	\N	\N	9be4882c-b05a-4f9d-91dd-9b3a57439bc5	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-08 23:10:34.191121+00
336	login_success	low	User successfully authenticated using password	1	\N	\N	dab5b3c5-537b-4cf3-8dc0-bad1e692a5e1	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 06:56:56.707172+00
337	login_success	low	User successfully authenticated using password	1	\N	\N	3bfceff8-6b01-4c71-b088-4198e9771320	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 07:14:09.981963+00
338	login_success	low	User successfully authenticated using password	1	\N	\N	a1f6a899-2f99-4a29-9031-2ef331f8cdcb	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 07:29:42.171436+00
339	login_success	low	User successfully authenticated using password	1	\N	\N	d4a1fe33-a1d9-44fe-953b-3439af068499	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 07:50:53.580139+00
340	login_success	low	User successfully authenticated using password	1	\N	\N	8718bd86-8c04-4d59-a3e5-924d0b5e922a	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 08:13:29.424554+00
341	login_success	low	User successfully authenticated using password	1	\N	\N	3f8f8964-fb6e-4d7f-8b2e-14fa6524d18b	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 08:37:27.851038+00
342	login_success	low	User successfully authenticated using password	1	\N	\N	c7d8cbef-501f-4895-8ec0-899966412b69	\N	\N	172.23.0.20	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 10:33:21.709105+00
343	login_success	low	User successfully authenticated using password	1	\N	\N	e1d0f9da-c4db-4086-90f2-e1065c6fafa0	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-09 10:51:55.722622+00
344	login_success	low	User successfully authenticated using password	1	\N	\N	97a9812d-6941-430b-8586-8957dbea7bec	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 03:04:18.450758+00
345	login_success	low	User successfully authenticated using password	1	\N	\N	36fc42a1-4091-4eea-9d70-953326d7d55e	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 04:12:00.480818+00
346	login_success	low	User successfully authenticated using password	1	\N	\N	2c44792e-3c0c-4179-a59e-5989e2e3154c	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 04:29:51.690041+00
347	login_success	low	User successfully authenticated using password	1	\N	\N	cf149acd-7d5b-469c-9f8c-ac6695e71fb3	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 05:42:25.727236+00
348	login_success	low	User successfully authenticated using password	1	\N	\N	bd83571f-bc92-4201-adaa-68d34bdafba9	\N	\N	172.23.0.17	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 10:01:05.239929+00
349	login_success	low	User successfully authenticated using password	1	\N	\N	aeeba679-3e0d-403d-9797-b3f3e9724347	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 10:30:41.861232+00
350	login_success	low	User successfully authenticated using password	1	\N	\N	81adc6ff-9925-4aa6-a33d-41d7ebf1bac5	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 13:06:53.378908+00
351	login_success	low	User successfully authenticated using password	1	\N	\N	1405100c-048e-4d50-8640-a9f765bd7f76	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 21:05:20.59187+00
352	login_success	low	User successfully authenticated using password	1	\N	\N	64531669-f9c3-40ae-9392-f6ba95328c8b	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-10 21:22:40.781456+00
353	login_success	low	User successfully authenticated using password	1	\N	\N	39b2ed68-9658-432f-bb53-9138153d2639	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-11 03:25:59.691867+00
354	login_success	low	User successfully authenticated using password	1	\N	\N	e364e220-60c0-40cb-aa9b-d282e0d74511	\N	\N	172.23.0.14	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-11 05:51:05.775007+00
355	login_success	low	User successfully authenticated using password	1	\N	\N	ef609486-48ed-424c-a8e6-a1087101f8f9	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-11 12:35:37.769511+00
356	login_success	low	User successfully authenticated using password	1	\N	\N	5c75de2a-4d8a-4a8c-b6b3-f25eb94b8b81	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-11 12:51:21.37334+00
357	login_success	low	User successfully authenticated using password	1	\N	\N	6403e868-b5f1-4ee0-9225-b14ff91508ef	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-11 22:10:08.354903+00
358	login_success	low	User successfully authenticated using password	1	\N	\N	d4d1b6a4-7fa4-4dfd-bb33-fe917b3b1fac	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-11 23:07:02.070548+00
359	login_success	low	User successfully authenticated using password	1	\N	\N	51cf0d54-064f-45e3-bc6f-5d05a55d392e	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-12 09:42:35.896259+00
360	login_success	low	User successfully authenticated using password	1	\N	\N	dfd76b14-e6cc-4af6-b969-ad2f06d54362	\N	\N	172.23.0.10	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) Gecko/20100101 Firefox/143.0	\N	/api/auth/login	POST	null	\N	{"login_method": "password"}	["authentication", "success"]	t	\N	2025-10-12 10:10:09.63255+00
\.


--
-- Data for Name: password_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_history (id, user_id, password_hash, created_at) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description, permissions, created_at, updated_at) FROM stdin;
3	manager	Manager with limited administrative access	["view_users", "manage_partners", "view_companies", "view_reports"]	2025-08-22 21:44:56.07414+00	2025-08-22 21:44:56.07414+00
4	user	Standard user with basic access	["view_profile", "edit_profile", "view_partners", "view_companies"]	2025-08-22 21:44:56.07414+00	2025-08-22 21:44:56.07414+00
5	readonly	Read-only access for viewing data	["view_profile", "view_partners", "view_companies"]	2025-08-22 21:44:56.07414+00	2025-08-22 21:44:56.07414+00
6	inventory_manager	Inventory Manager with full inventory access	["view_profile", "edit_profile", "view_partners", "view_companies", "access_inventory", "manage_inventory", "manage_products", "manage_stock", "manage_warehouses", "view_inventory_reports"]	2025-08-23 04:26:22.064979+00	2025-08-23 04:26:22.064979+00
7	inventory_user	Inventory User with basic inventory access	["view_profile", "edit_profile", "view_partners", "view_companies", "access_inventory", "view_products", "view_stock", "view_warehouses"]	2025-08-23 04:26:22.064979+00	2025-08-23 04:26:22.064979+00
8	sales_manager	Sales Manager with full sales access	["view_profile", "edit_profile", "view_partners", "manage_partners", "view_companies", "access_sales", "manage_sales", "manage_quotes", "manage_orders", "view_sales_reports", "access_inventory", "view_products", "view_stock"]	2025-08-23 04:26:22.064979+00	2025-08-23 04:26:22.064979+00
9	sales_user	Sales User with basic sales access	["view_profile", "edit_profile", "view_partners", "view_companies", "access_sales", "view_quotes", "view_orders", "access_inventory", "view_products", "view_stock"]	2025-08-23 04:26:22.064979+00	2025-08-23 04:26:22.064979+00
10	purchase_manager	Purchase Manager with full purchase access	["view_profile", "edit_profile", "view_partners", "manage_partners", "view_companies", "access_purchase", "manage_purchase", "manage_purchase_orders", "manage_suppliers", "view_purchase_reports", "access_inventory", "view_products", "view_stock"]	2025-08-23 04:26:22.064979+00	2025-08-23 04:26:22.064979+00
11	purchase_user	Purchase User with basic purchase access	["view_profile", "edit_profile", "view_partners", "view_companies", "access_purchase", "view_purchase_orders", "view_suppliers", "access_inventory", "view_products", "view_stock"]	2025-08-23 04:26:22.064979+00	2025-08-23 04:26:22.064979+00
12	accountant	Accountant with full accounting access	["view_profile", "edit_profile", "view_partners", "view_companies", "access_accounting", "manage_accounting", "manage_accounts", "manage_journals", "view_financial_reports", "view_sales_reports", "view_purchase_reports", "view_inventory_reports"]	2025-08-23 04:26:22.064979+00	2025-08-23 04:26:22.064979+00
2	admin	Administrator with user and content management access	["manage_users", "view_users", "manage_companies", "manage_partners", "view_audit_logs", "access_admin_dashboard", "settings.access", "menu.configuration", "inventory.access", "sales.access", "products.view", "stock.view", "warehouses.view", "receiving.view", "quotes.view", "orders.view", "customers.view", "invoices.view", "products.manage"]	2025-08-22 21:44:56.07414+00	2025-08-22 21:44:56.07414+00
1	superuser	Super administrator with full system access	["manage_users", "manage_roles", "manage_system", "view_audit_logs", "manage_companies", "manage_partners", "manage_currencies", "access_admin_dashboard", "settings.access", "menu.configuration", "inventory.access", "sales.access", "products.view", "stock.view", "warehouses.view", "receiving.view", "quotes.view", "orders.view", "customers.view", "invoices.view", "products.manage"]	2025-08-22 21:44:56.07414+00	2025-08-22 21:44:56.07414+00
\.


--
-- Data for Name: service_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service_tokens (id, service_id, token_hash, scopes, expires_at, is_revoked, created_at, revoked_at) FROM stdin;
1	1	353a2c3ece069812c47221ee1fc5890c246171ec6dc561a1d3ee6181d642ea68	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 00:58:28.685659+00	f	2025-08-24 00:58:28.401761+00	\N
2	1	20c870b5d005a3c762002cb3f69d7b12a44576f113d52a4a38cd81778807660e	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 00:58:48.033597+00	f	2025-08-24 00:58:47.751628+00	\N
3	1	ab84b2df8126024a7ab7939f1c309f23060adc58635b6e3d02545fb20b16022d	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 01:07:24.389448+00	f	2025-08-24 01:07:24.100547+00	\N
4	1	303cbbe86e2c444b2b886ac7ed54865979e80cf9c0e3769313c4f2d67501777e	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 01:40:48.997265+00	f	2025-08-24 01:40:48.713555+00	\N
5	1	a6acd3f5fec7289c3b4b2c76573dd84de0b75548f6f5cb0524c498a4fbac2eb1	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 06:09:03.759777+00	f	2025-08-24 06:09:03.476372+00	\N
6	1	1d4a8bb3f85631055390e48526776cfac30684a92d55098839eb2b89e530569e	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 06:50:46.463285+00	f	2025-08-24 06:50:46.161177+00	\N
7	1	c4a4371379bb815a576073b4fe45073400619d2168470ee68acf4e47532f4b52	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 07:13:26.599119+00	f	2025-08-24 07:13:26.311623+00	\N
8	1	88fd2ec3c1b358c99b4181620a22723402b0384f595bd94719a42f7543c1c135	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 09:47:41.212437+00	f	2025-08-24 09:47:40.929658+00	\N
9	1	715c977c4aff8a5cb9df231e9f40cfd16f8e1b5bd0bba91b754e02b164ead25c	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-25 22:49:47.931113+00	f	2025-08-24 22:49:47.648035+00	\N
10	1	02841694fbec0ffaba17332689f02d7539b03768afa4b6036496cb629ddaba1c	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-08-31 23:56:57.925448+00	f	2025-08-30 23:56:57.636325+00	\N
11	2	72502ae7f7d90497d74365747ce035edbbad56db8cd9b4912cbc23f07d726cfe	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 04:41:28.56346+00	f	2025-08-31 04:41:28.280648+00	\N
12	2	48662b7878cc48259dff913b68ee7616b18e10e6e922b1f094ab3d5f2d1e79fb	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 05:06:41.592906+00	f	2025-08-31 05:06:41.31006+00	\N
13	2	5663f6063a8c8e174dc015354fd2ae0989adc01f8c340c80c342e64e6454a1a8	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 05:21:28.529704+00	f	2025-08-31 05:21:28.237579+00	\N
14	2	d7ccd92c8d176087c0bbfb786478af3b7f18c2613cdd1b343934c432ab2ddb52	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 05:22:26.670779+00	f	2025-08-31 05:22:26.389354+00	\N
15	2	c07f8f09007d12444cef4a0a870ed67069f3f0e0627772782f5d543a95f69821	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 05:23:36.936308+00	f	2025-08-31 05:23:36.646823+00	\N
16	2	d31e288edccec0bd9160823e61b7d007438ffd7baf7377ca8895be3e93cbec9b	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 05:24:58.578178+00	f	2025-08-31 05:24:58.294482+00	\N
17	2	e7fda02b5639f32eebbf627fa6906f1ff055c0ca58963d068f2c73e839f39400	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 05:42:07.012586+00	f	2025-08-31 05:42:06.72977+00	\N
18	2	4ffd7c66237203c92b71934d2dba99c7f586734e79a8d1c43511e010d20ab110	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 07:05:39.979287+00	f	2025-08-31 07:05:39.679118+00	\N
19	2	9e7a6e683e06c0cb1c4232e2b7f271924f5b32cc2058b91575003a9a08969e15	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 07:07:27.677881+00	f	2025-08-31 07:07:27.383395+00	\N
20	2	9e74642de4ca594018ea25d5863730f6cc0b2101b546d6e0b7812eedbae53e30	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 07:11:37.186237+00	f	2025-08-31 07:11:36.889856+00	\N
21	2	d9b81f905980bddc852c613f79375c92ee2a6eb5f5a7be43db6a2629a032d4ac	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 07:26:04.660579+00	f	2025-08-31 07:26:04.367894+00	\N
22	2	f841c82ae667755f4a8c8569555bd61fa9da6fe2d38738be7b975356fcb1e42a	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 07:54:47.127505+00	f	2025-08-31 07:54:46.828351+00	\N
23	2	ab62a6f73236bbd1a9c6db8a3cc49aeb0c4472a85b6c1a0e49e87369a401125a	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 07:58:12.808387+00	f	2025-08-31 07:58:12.524345+00	\N
24	2	879bc899556ec7514a2416659880fb77272af32e93fde22f859b1d51d161f295	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 08:05:27.899447+00	f	2025-08-31 08:05:27.612315+00	\N
25	2	770ae5ddbf985e859ec134ff263737182d707ddf01d6271cc6a8d2dd88348d13	["validate:tokens", "read:users", "read:permissions"]	2025-09-01 08:59:40.025624+00	f	2025-08-31 08:59:39.734064+00	\N
26	2	9873845bca2170f4fc6c95c701e6d94bca844e90675ea1dd5e50598f0bc1d83a	["validate:tokens", "read:users", "read:permissions"]	2025-09-02 09:29:00.601575+00	f	2025-09-01 09:29:00.318169+00	\N
27	2	58b24465e269cd7a8cdf9bf3b5b0e0227a708909456987a3a5b2f8437803dfe9	["validate:tokens", "read:users", "read:permissions"]	2025-09-02 12:52:36.385062+00	f	2025-09-01 12:52:36.103462+00	\N
28	2	e2d8c6c3e74e9916f4b91e1f667bca515fe6a540276c6cd81be6e35413605639	["validate:tokens", "read:users", "read:permissions"]	2025-09-02 14:02:51.885326+00	f	2025-09-01 14:02:51.603645+00	\N
29	2	d08b1ab83cb3faa44e14ae12c0c2b36993f53ff451b34c65beb195f0099d4ff6	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 01:46:43.616843+00	f	2025-09-02 01:46:43.335578+00	\N
30	2	0cd839827bfa6aff02246a96333779efa423ab51237fbde2246da465e2c5a841	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 02:04:44.824671+00	f	2025-09-02 02:04:44.542027+00	\N
31	2	9d8cd40f70acedb2ca667768c6caa944f8ebfea202121c49c713c3a2e33302ab	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 03:11:26.645079+00	f	2025-09-02 03:11:26.362376+00	\N
32	2	49d9025d123de1b0b2e793f745a35062833bb7b10024105cb92612e8ba7201c0	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 03:50:08.918875+00	f	2025-09-02 03:50:08.635597+00	\N
33	2	17c51b93d68e28452fea9173bf1259589e0c2b567e0597bdb3c266679b9a1d06	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 03:52:17.18939+00	f	2025-09-02 03:52:16.891409+00	\N
34	3	b6f27d15555904414472cfe54c6fe70721216db496a6299e2db6f64a7bcd44e1	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:02:43.409301+00	f	2025-09-02 04:02:43.124056+00	\N
35	3	049a8de8bde5fae9a5923e1e03d4dea14ea7542610e1e193fb12369d24507040	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:03:41.978668+00	f	2025-09-02 04:03:41.675452+00	\N
36	3	8cdd67d3303437387e588046c4f1067106177de9d480935db5e7c33b04e83afa	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:05:03.849252+00	f	2025-09-02 04:05:03.567426+00	\N
37	3	a3985aaefa56e8032d6413d4b876c5c1a136954ac63c7ae25e705519b43f943e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:08:09.304038+00	f	2025-09-02 04:08:08.99145+00	\N
38	3	0630df02cf7775e2fea9177b05eecd63ef62f868cb19080799f5fa6b3627eee5	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:08:25.051603+00	f	2025-09-02 04:08:24.760948+00	\N
39	3	c1470d037938ceb3a237157641c63aca56ffe739123406eaef94c32a49246295	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:09:13.249532+00	f	2025-09-02 04:09:12.958059+00	\N
40	2	808488a1493951cc0ee649bbb5fd0cb7b72a2677eab175752634307263341940	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 04:09:13.608043+00	f	2025-09-02 04:09:13.311575+00	\N
41	3	1648becf33701474849ac069eb90271d15344847f69959d5f9f0038eb189b592	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:09:29.744984+00	f	2025-09-02 04:09:29.454813+00	\N
42	3	3e9d9c504d9a95d7498aae75934bfdf8de82a2f88d682c87df3d084e2abe4270	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:11:27.093458+00	f	2025-09-02 04:11:26.796811+00	\N
43	2	6ffa9c7df1bcc905c8fce8dafed64ad6524e2757991c131c34154676d9f2aba8	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 04:11:27.631908+00	f	2025-09-02 04:11:27.156916+00	\N
44	3	b5417bd8f6a0529662cb25a8c32c6eaefc6d03d07aeb6649ead935a75fac6325	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:11:37.10132+00	f	2025-09-02 04:11:36.799207+00	\N
45	3	28b7a4309376d9e1325f071434760a24e73c2d5179ca725574f38b236ac03114	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:12:54.225907+00	f	2025-09-02 04:12:53.928347+00	\N
46	2	3db3876ca7393cab7efde7eb750809a07ca7b0e5919155b11624fb57ea50b65c	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 04:12:54.601638+00	f	2025-09-02 04:12:54.30042+00	\N
47	3	7d9c41f757e16d6758d8322a55b79bb7356ff0689ca7df7aaf4b163f9afa52f7	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:13:14.514248+00	f	2025-09-02 04:13:14.224965+00	\N
48	3	6cc59c91c9835871430b71783a17eda2b7fab179047643dc88d91be88929c149	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:15:27.054022+00	f	2025-09-02 04:15:26.749498+00	\N
49	2	10cca4db0d6b6ba67bcf606470bcd9177108c51ff786d80b9e7bca532c7322ae	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 04:15:27.411796+00	f	2025-09-02 04:15:27.115744+00	\N
50	3	6a87d72dab9d9f80c4cfb45d579f59f3251d7725051cf88e9259fd1d9f093818	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:15:57.743667+00	f	2025-09-02 04:15:57.447585+00	\N
51	3	68ef89fb9750758fb7800fdd65a8e0081c64d124690d07dbefde0dde1d2cb43b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:17:43.822663+00	f	2025-09-02 04:17:43.527545+00	\N
52	2	f9cbc5d613ecb5757a02ce612e87c34bbf271f45832c07404a04753d72eb48ac	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 04:17:44.193116+00	f	2025-09-02 04:17:43.892407+00	\N
53	3	561c17e457181e9a2b315157fad0f296ba1933108aeba7f1a35b2c260ad71fd9	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:18:07.003121+00	f	2025-09-02 04:18:06.710235+00	\N
54	3	5bafb6dfd8632f01264337688772b6b967a3f59ac94a68f9e00a7b088fc9c174	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:18:22.881961+00	f	2025-09-02 04:18:22.593531+00	\N
55	3	41c202458eee0755d97d0d39d77b7a325edf1dcff599895a5eccc78629113095	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 04:19:07.754019+00	f	2025-09-02 04:19:07.472342+00	\N
56	3	139ee88a720627d051bebc4f9aa6c9d79695f2c4218b6cc5c9dbd4a535aeb616	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:18:31.11976+00	f	2025-09-02 05:18:30.799187+00	\N
57	2	c7dec96c3023b03f2b6d1e750251f661ac08146516b5a471e8ae081b656cc414	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 05:18:31.502881+00	f	2025-09-02 05:18:31.214047+00	\N
58	3	7da8dec153da0b400b510c51f8ad1cf7b6a629403cb45de17785cbafb6aa1364	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:19:41.459595+00	f	2025-09-02 05:19:41.155358+00	\N
59	3	eb7751953c4804f3e4c44c984682f70f169bb755830551f4cc764754d00f1975	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:19:55.585378+00	f	2025-09-02 05:19:55.289056+00	\N
60	3	940ae77408b2460646c23885e0aeb637daab7bfb1e0cee0404c2a4db53a3ea7b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:20:30.198533+00	f	2025-09-02 05:20:29.87687+00	\N
61	3	022e56a9b6bf8d95f97711d4e10348a4a6fe4d34649e4f4af51ba7f1d35a77d8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:21:14.002018+00	f	2025-09-02 05:21:13.713665+00	\N
62	3	e6e8d724ac720f3f45552e9ed29ad6c59ca520995fd235032727211adf3ef3e0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:21:45.3589+00	f	2025-09-02 05:21:45.069758+00	\N
63	3	0c6b5f67dc441a555029858dffbf955d52fe69d3ee2b445ab942b8ba4ccbee2f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:22:03.221126+00	f	2025-09-02 05:22:02.934483+00	\N
64	3	639843d41fcdcc200645e443a27fb1ede07871094e25c0879be3df64fcd49459	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 05:23:11.119331+00	f	2025-09-02 05:23:10.83828+00	\N
65	3	06562de616cd33c37e7b559663862d3b332fb1f7e3b8131b4ca3e07992379009	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 06:22:38.806354+00	f	2025-09-02 06:22:38.479618+00	\N
66	2	5d23c3fc495cbe829fb4d7869b1f0d75fb856e088f3a8b20f33f4993aafb6e36	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 06:22:39.157158+00	f	2025-09-02 06:22:38.874005+00	\N
67	1	65c4901e94f7a2642bc3f075c9e58404bc564ae7613819f2ae812e140be75ec6	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-03 06:22:41.216687+00	f	2025-09-02 06:22:40.929732+00	\N
68	3	a98cbdf425ec46a668f0c21bdd647fb6e31a047d950c7ef8374ef474fb83b70a	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 06:43:35.234588+00	f	2025-09-02 06:43:34.946549+00	\N
69	2	8fe3b5477e1b862863dc412296244bf8bc55019187d2cb0928edbd56648479c4	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 06:43:35.573435+00	f	2025-09-02 06:43:35.279336+00	\N
70	1	0c8f24c0fff4c6571053d28e493dcdc4cd3487806dc31eb004b5f45b8e13ad92	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-03 06:43:35.911151+00	f	2025-09-02 06:43:35.627479+00	\N
71	2	30adcd4049b12aa8cf95daa93b0b3d3f74aeea3695577233a4f7cce662c72811	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 06:47:29.920648+00	f	2025-09-02 06:47:29.530754+00	\N
72	3	b05e6a38e93ab2c6f6256dafdaae8d90fe835e8a2c1c069d431e8824ab6025c7	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 06:47:30.220452+00	f	2025-09-02 06:47:29.931512+00	\N
73	1	54e86973be16aa991eb88ff4f1558d930c4dff84e249e9ff3cb3d7aa7889a75e	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-03 06:47:33.022886+00	f	2025-09-02 06:47:32.727194+00	\N
74	3	1e0f5339a29c28a72a1ce56f7ef438cbbf75ae5c643f01ec01ac424a7fbba6d4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 07:10:36.416521+00	f	2025-09-02 07:10:36.129372+00	\N
75	3	de89361b6d97fdc6d3c61c8ddd0bb95553af04bcb7fc355252543b89082c4d6f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 07:49:20.335837+00	f	2025-09-02 07:49:20.048365+00	\N
76	2	fdb498814f90c2fa4b2cbd030c95488d1c7870075fbc9d9ed095401baef08911	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 07:49:20.670645+00	f	2025-09-02 07:49:20.374936+00	\N
77	1	7526213c99ca7c217a539016c0ff4a8c0e723ad884264a0695cd7ff8a588ae75	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-03 07:49:24.382505+00	f	2025-09-02 07:49:24.082448+00	\N
78	3	8b4460df8acf5901abeabbbbebaa3cd1b44abfcaa2dd5a3844bf965cb9b3e674	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 09:00:52.736131+00	f	2025-09-02 09:00:52.445572+00	\N
79	2	eb0904668c04f40cab15bcca395176b77814e37e96ad58678aefddb469502b91	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 09:50:19.137508+00	f	2025-09-02 09:50:18.855048+00	\N
80	1	0bc380257ca5f83e6eb339c6f3af3ab0fb4ae63fd29aedf6924c856fd4d2d62b	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-03 09:53:08.609171+00	f	2025-09-02 09:53:08.280099+00	\N
81	3	6379cb1bfd5e8a162169089192974ef696bd449941314ead9c778a71454128c8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 09:53:09.594702+00	f	2025-09-02 09:53:09.152729+00	\N
82	2	0ae3e497be59c0d3c86d4c57472d9f3f7d74442ebba9ba19e669d60b40ac2dc5	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 09:53:09.93056+00	f	2025-09-02 09:53:09.643475+00	\N
83	1	af7e20f0f9243530c69cda8f7bf16461dfed20ec37f7d528d6afed694787dae6	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-03 09:56:38.278299+00	f	2025-09-02 09:56:37.983613+00	\N
84	3	f73f54ec017364ed20b8ecd8654682c05b07016e991540714517296c905130a2	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 09:56:40.18115+00	f	2025-09-02 09:56:39.895141+00	\N
85	2	704d96b991aa895db2cd2e631f833ce1594f09fcd95cb6d5e31a042c61de4e6c	["validate:tokens", "read:users", "read:permissions"]	2025-09-03 09:56:40.500814+00	f	2025-09-02 09:56:40.217282+00	\N
86	3	d8d949add35800994d954e65d4cc0e4aa943b0e37470d514c7a99bc813856342	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 14:18:56.921194+00	f	2025-09-02 14:18:56.635504+00	\N
87	3	84d512258e92b691ca84ca5047f7e12da1585d6eef30a71ef339d65163a4f5fc	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-03 21:45:11.676676+00	f	2025-09-02 21:45:11.332993+00	\N
88	3	7966913065f4094936660499b70f26b5cd4bea317fe0481caea9d13b659e0778	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-04 04:03:41.586591+00	f	2025-09-03 04:03:41.29886+00	\N
89	3	727a1dbe57eb87079f26c227332861545319aea9ed60cc754fee7829ec4523cb	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-04 04:10:55.218239+00	f	2025-09-03 04:10:54.934966+00	\N
90	3	ca3b80482f1a042dba6f1fb475b7f885f507a0091c0b6516536632ba71316589	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-04 04:12:17.95871+00	f	2025-09-03 04:12:17.675929+00	\N
91	3	bde19f87f46d8eb46d120728d2ef8088f2d89f8d1ff7b64ce0f79c0efe2e3c9f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-04 05:02:23.226836+00	f	2025-09-03 05:02:22.92009+00	\N
92	2	c52b954b8d6fcec4120cb8c808c830efb55bb951b6fdb5f3125f87e85563d5ae	["validate:tokens", "read:users", "read:permissions"]	2025-09-04 05:02:23.581594+00	f	2025-09-03 05:02:23.287482+00	\N
93	1	b2df47ff8319462ab13e80f5317a6172ec56bd8e0082287a58505d393da8ddef	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-04 05:02:25.386502+00	f	2025-09-03 05:02:25.100628+00	\N
94	1	819d01ce5644b250303232b1f8ddae39ba28df8bb0ad115998e9771fe3282372	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-04 07:44:43.055176+00	f	2025-09-03 07:44:42.75547+00	\N
95	2	5f76a03528783083904de387b2b41370ca4923d8b13ba814e94565c2914ec7d4	["validate:tokens", "read:users", "read:permissions"]	2025-09-04 08:09:18.191939+00	f	2025-09-03 08:09:17.909828+00	\N
96	3	c70fb79354d8d6f6c5541d9d5c0cf70b6459a0caa067541aaa8d6f59bd57c14a	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-05 08:10:07.958766+00	f	2025-09-04 08:10:07.676664+00	\N
97	3	75d263b4721787e6ed42684f594c939d78bc8eefd5d04911cb1e2c5e92c1b945	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-05 22:21:04.477881+00	f	2025-09-04 22:21:04.185766+00	\N
98	2	efdc7e610a37e9577a85cec2d06fb2dde6c66bf5e5b75813e48a902c6fd26c07	["validate:tokens", "read:users", "read:permissions"]	2025-09-05 22:21:04.819692+00	f	2025-09-04 22:21:04.534909+00	\N
99	1	6ae85c053fb2f1353701eebed0b5b09b8d32bb4e58f43f0de7d438b1828b0fa7	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-05 22:21:08.134503+00	f	2025-09-04 22:21:07.851661+00	\N
100	2	4899069b3c9ed00fc0da4f7e3666f1a4e77ac5e3f79610631674a7d8097e027e	["validate:tokens", "read:users", "read:permissions"]	2025-09-11 08:57:28.676506+00	f	2025-09-10 08:57:28.394864+00	\N
101	3	b4a8eefe9570d529e3d814b1f42156367064746113c799ed3c1d1df380669c55	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-12 03:49:23.233844+00	f	2025-09-11 03:49:22.951577+00	\N
102	1	13e3a90d40e7c20b2ae5704a3295321d9bca0eb86bbf2ea9a4f6884be5df83ab	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-12 03:50:37.150404+00	f	2025-09-11 03:50:36.860724+00	\N
103	2	095be6be87bcfd67513f09e3cdb95aad46b4c353d1e1ec727701a47a6e0338b5	["validate:tokens", "read:users", "read:permissions"]	2025-09-12 03:53:30.540699+00	f	2025-09-11 03:53:30.258062+00	\N
104	3	8aa7744510e695cf7c7c148f1358df8cdbd37319f5271321003949eb03ba660d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-12 04:15:08.99725+00	f	2025-09-11 04:15:08.714476+00	\N
105	3	fb5fa97f58e4ff9bb2fc1b53662d1f26c1e783697060f705420139200a315121	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-12 04:19:55.221141+00	f	2025-09-11 04:19:54.928988+00	\N
106	2	d47238c4ce45035f0af762577582a6983998f6dd7d8364ea01f4579d6936e497	["validate:tokens", "read:users", "read:permissions"]	2025-09-12 04:19:55.597633+00	f	2025-09-11 04:19:55.271467+00	\N
107	1	de8088a0dbcde7997134af6816636f8182cebaaa99016119f3334520f54bbca0	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-12 04:20:23.914801+00	f	2025-09-11 04:20:23.633553+00	\N
108	3	ab3aebc66dd6877b02df9d68ed875a37943caafe83888b92c60878a00170d1a8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-12 04:26:57.887947+00	f	2025-09-11 04:26:57.600722+00	\N
109	3	baf6364d23b20a24c0847ee7fd619cbdd5dafb6ba8cc44bdb9d12a672260e402	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-12 07:47:55.492456+00	f	2025-09-11 07:47:55.20858+00	\N
110	3	fb7cef5ea4d6bece00f53d99e02e63e61feb574524b0ab59c28648988009f2bc	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-13 00:20:40.957437+00	f	2025-09-12 00:20:40.675199+00	\N
111	3	f2aed31abbf09674682d9cca8b0aee8ca343cd7204364af9d4695e3b5306ad15	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-13 00:21:57.861242+00	f	2025-09-12 00:21:57.57975+00	\N
112	3	c4aa7160425dcc778bcbde896fc45c3d12ba759a6df26847a495469df21dae37	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-13 00:47:34.846114+00	f	2025-09-12 00:47:34.563152+00	\N
113	3	8f9c7811d443050d8ebbf8fbfe9c2e33778b1f09f68c81b7c5f500fe92c4c0a9	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-13 00:50:47.695413+00	f	2025-09-12 00:50:47.414342+00	\N
114	3	5d85e2dcb041edee200d1264279a3005d6c47a845cc7c266fcfbba6c98e7d43c	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-13 00:52:06.579754+00	f	2025-09-12 00:52:06.297733+00	\N
115	3	d195fb058d565c63dddada76a9565bf1528797cbc496b93452d4200567806746	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-13 00:52:49.249218+00	f	2025-09-12 00:52:48.968037+00	\N
116	2	ed6c41b4429af107aae0d0b0e4c22290a31a1927ea8804da05dc7554239b2428	["validate:tokens", "read:users", "read:permissions"]	2025-09-13 00:55:10.550653+00	f	2025-09-12 00:55:10.248662+00	\N
117	1	f2adabbbf3ccead9f0a9ad7e96cb87f1118834db69f5cd00eb6e1d96d4e6f568	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-13 00:55:12.88156+00	f	2025-09-12 00:55:12.588805+00	\N
118	3	c644277f30cfc510bd361cf70765402e6e4c4b4229afaee39cefa54eaeba48a1	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-13 22:53:21.579751+00	f	2025-09-12 22:53:21.28014+00	\N
119	1	887c131fc2af3f6d3afad74690ccd690660941c12fee2e8e2e0f795c29df5475	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-13 22:53:22.552972+00	f	2025-09-12 22:53:22.26954+00	\N
120	2	f2c2b07e5c64c60bb34147dec36ad4fa9514a26b12024b66df557fb504509e4e	["validate:tokens", "read:users", "read:permissions"]	2025-09-13 23:10:34.5141+00	f	2025-09-12 23:10:34.231392+00	\N
121	2	7918294d756a377daa1ef2f65fe3e378bd10f00581b33a21ff835c0ad49d897f	["validate:tokens", "read:users", "read:permissions"]	2025-09-13 23:13:06.251097+00	f	2025-09-12 23:13:05.969288+00	\N
122	2	059242ce570410e2f543761d3fe4c8098dabbaac982d5ca7267cb7fafd27bfe1	["validate:tokens", "read:users", "read:permissions"]	2025-09-13 23:24:03.993722+00	f	2025-09-12 23:24:03.709603+00	\N
123	3	bc9c4eaf89a04453b3940cf0ebb29218b766cb5145f75e03620ed6d871de1a0e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 02:37:00.488153+00	f	2025-09-13 02:37:00.199103+00	\N
124	1	d9793b64c66adedd459a2cc674f7806610aa25a8dc6dc66f3312a64e5ace066d	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-14 02:40:44.767738+00	f	2025-09-13 02:40:44.480408+00	\N
125	2	5aad7f761509ab10699cc38f5a3b0ad6e922a051c18cf4fe59e3d29730e7db12	["validate:tokens", "read:users", "read:permissions"]	2025-09-14 02:41:23.255193+00	f	2025-09-13 02:41:22.974216+00	\N
126	3	0b67d8b59b92780584ee457da821fc132a8f54ba3f3748330f03b213b5ee9ce8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 02:47:04.605266+00	f	2025-09-13 02:47:04.323235+00	\N
127	3	936fefb0dc635d3d4e48001197332b50e50422335ac0f2eba01a6dee2222b6a6	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 02:47:46.416191+00	f	2025-09-13 02:47:46.135232+00	\N
128	3	ea43e21b10f468ef37f8c92defc5363b68df3fcf6d5d70dd8478fa8d97a8bd14	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 04:50:26.040499+00	f	2025-09-13 04:50:25.753836+00	\N
129	3	a9990172da706bf386760554e96440f9f4bf1b3b3450a1833cfae6083e742ce0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 04:52:04.256711+00	f	2025-09-13 04:52:03.961731+00	\N
130	3	69713e1de2ee24e37427c3e79920bf1f576f4fb2fefb6e5e5aa5a95f1209dcb0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 04:56:12.388244+00	f	2025-09-13 04:56:12.079965+00	\N
131	2	3ac2e9938fdc269d8afd55d6fd70896b6e3306bd46b0238f620ba588c78fc8a7	["validate:tokens", "read:users", "read:permissions"]	2025-09-14 04:56:12.726569+00	f	2025-09-13 04:56:12.440785+00	\N
132	1	094c5b7e62bc6964a8c6c5b208498cec268ce63c91c8c366946931524994c495	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-14 04:56:15.284401+00	f	2025-09-13 04:56:15.000547+00	\N
133	3	deda6272a062239aad997c3fe98517b31325c3a03461b9884df0df1d8287f393	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 05:00:56.293021+00	f	2025-09-13 05:00:56.011088+00	\N
134	3	0631f80ed8469ddf2e8f161ab10076773ed3cbe75165c0dc18adfab032c88647	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 05:01:13.482367+00	f	2025-09-13 05:01:13.199068+00	\N
135	1	79d43f0da2b5b991097bbcdff8cc83186bb55d91f3bcd2d26fba00c7fb42b840	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-14 05:05:31.14553+00	f	2025-09-13 05:05:30.847638+00	\N
136	1	e3bea1286a175705bb35e165c59e8b3440ad299d699f14f621388114431d8289	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-14 05:06:01.366787+00	f	2025-09-13 05:06:01.063982+00	\N
137	2	fb3b0303769f30e30d1c2734931b054957273d4a34ab7f77a89fb3f588289fbd	["validate:tokens", "read:users", "read:permissions"]	2025-09-14 05:06:01.769651+00	f	2025-09-13 05:06:01.448791+00	\N
138	3	79fb31ff947849003210b4cc6cca0fb6b792f6ba5c97f144abafae2022fb4c5e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 05:07:23.761706+00	f	2025-09-13 05:07:23.477912+00	\N
139	3	7a4e556dcedd84b873856e2a251a21bd0dbed46952b0ecef419a56d298125f27	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 05:07:35.352683+00	f	2025-09-13 05:07:35.07128+00	\N
140	3	e6c53442ffc87af7037d14015641980e4873ff701a6ae0dcda25e28df5502a9a	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 08:51:58.673152+00	f	2025-09-13 08:51:58.38244+00	\N
141	3	22adc19f1eac00698f07bcb8de057aba17b9dea9b6f01dbf393f6c8ef35592f2	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 08:59:58.665602+00	f	2025-09-13 08:59:58.384282+00	\N
142	1	a119a7d6b1c545b72ab05f339e14fe7e5ef480a9837f79106220adc2f171f11c	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-14 09:05:07.776458+00	f	2025-09-13 09:05:07.460882+00	\N
143	2	6588a8bceafa33dd07be9eff55ceb257fdecec3da65eddd29e26cde66884ab45	["validate:tokens", "read:users", "read:permissions"]	2025-09-14 09:05:16.116575+00	f	2025-09-13 09:05:15.829639+00	\N
144	3	0c53489efd41596a7e07ce4b78ddaf99c89bea2d6a36c3a556f048dee8b027ee	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-14 09:06:25.606239+00	f	2025-09-13 09:06:25.325331+00	\N
145	3	acb4d04183e952ba9f81d4fe84a32ff37f5c28edaf40de5e84d4a2a1244b1080	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 12:41:40.454532+00	f	2025-09-14 12:41:40.152321+00	\N
146	2	54c83f30dd9d394dac388405d376f55715244a5b0542566b21bc86469a02df83	["validate:tokens", "read:users", "read:permissions"]	2025-09-15 12:41:40.808557+00	f	2025-09-14 12:41:40.518993+00	\N
147	2	446ec759cb34750518721c9df4f8842d8f4fcfca603107a121be386c882b21d8	["validate:tokens", "read:users", "read:permissions"]	2025-09-15 12:41:41.113697+00	f	2025-09-14 12:41:40.821753+00	\N
148	1	4cecb221db122b0895dcee81387956b11a25330fd1b8fa4f5c1d08996c3c50a0	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-15 12:41:41.602519+00	f	2025-09-14 12:41:41.286851+00	\N
149	3	9233e87388f83e71dbbeb183395294e0d317c237b5398648b7ba795a84b6df1d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:14:24.66246+00	f	2025-09-14 13:14:24.372811+00	\N
150	3	5cca52d3c8af179e62583aa2f8daf1ece6cffbcdd532fc8afec42c62646d1aca	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:15:46.468999+00	f	2025-09-14 13:15:46.186883+00	\N
151	3	6f3060367b4be1e038b68c1ea86e73356d3c0b1578836b2dd68b1281ea8f1a8b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:18:11.982991+00	f	2025-09-14 13:18:11.700584+00	\N
152	3	58374ac9a10955967f8acdd925286d89e24742a47a5e474c62385f9493dfc5d4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:26:46.333431+00	f	2025-09-14 13:26:46.04743+00	\N
153	3	776d4c37e6c843b6b1bc1ed233f317f3a4b17816ccde18e935106542fb26becf	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:26:58.659604+00	f	2025-09-14 13:26:58.378131+00	\N
154	3	6632cea714f4df61c164abe23dd1af2b0ca90fa18cf25845685aa87a148861e4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:27:30.378454+00	f	2025-09-14 13:27:30.096821+00	\N
155	3	8d682406af465818249daf6a0f123caa75aa7c34fad5a71bbae3424421ce267f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:27:59.499118+00	f	2025-09-14 13:27:59.215752+00	\N
156	3	e6517b2fe9498ca7b262b374dd7dfe1c67afa2ed9490d256c31de55abebc7b78	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:30:06.716758+00	f	2025-09-14 13:30:06.434569+00	\N
157	3	a71a0b4dbb6cd4eafc09fc420916330bd722a56dce70a5269f0be6a57887bb81	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 13:35:28.449564+00	f	2025-09-14 13:35:28.167243+00	\N
158	3	2cc39c7ee6a7f7236929b62b9845e6e8305d52cded3e1c335086580a6833c66f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 21:25:47.659056+00	f	2025-09-14 21:25:47.377563+00	\N
159	3	324b4c74a2118d937ccd477641e0cb6bb640c86f566453c77fd1a4b9143e1ad4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 21:28:14.290694+00	f	2025-09-14 21:28:14.006778+00	\N
160	3	cacef3c47feea352fe23d8d31130d842b8a5041c800e9d2794e4254947599d11	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-15 21:29:17.855376+00	f	2025-09-14 21:29:17.572299+00	\N
161	3	2e4c6d665e38b152016efea634ca1252e68b94f9faa9420cc789adc8f8e66103	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 04:24:38.0705+00	f	2025-09-15 04:24:37.756911+00	\N
162	3	454c4dfe74744915b6f11571d2aa39ff912cd60f70fda7a3298206c2fe1d9a07	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 04:38:04.454996+00	f	2025-09-15 04:38:04.172402+00	\N
163	3	edf5627967fcf97783af8d90ba01d44e94d367c4f9e71f5fb186a79159a04f8a	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 04:39:46.948862+00	f	2025-09-15 04:39:46.666739+00	\N
164	3	b8d4cab7125d8fef574cc87b2be995299bb912e69da82df82b070d9d5c3d42ad	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 04:47:15.565057+00	f	2025-09-15 04:47:15.283914+00	\N
165	3	385a7e79e2e18022b982c9691bcbd4dec251d2cc0fd80eba4ae9d33725fa6ff0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 05:11:50.115277+00	f	2025-09-15 05:11:49.831798+00	\N
166	3	6a19dd36ccbafbb01de8e87bdf7f77c6d05cd7a3be6b11fed17749c06e01ae24	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 05:15:49.618088+00	f	2025-09-15 05:15:49.335322+00	\N
167	2	6dd5ad089b885b7a158de5841bb8c2a7136f05f9abc73c0163f4026b0ac19814	["validate:tokens", "read:users", "read:permissions"]	2025-09-16 05:15:49.996091+00	f	2025-09-15 05:15:49.714057+00	\N
168	3	2d490f3583ab8ed1af32a093a4b750aca308d1f661b48a194d2f623c090490d1	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 07:43:56.303462+00	f	2025-09-15 07:43:55.978522+00	\N
169	2	9a82b74f9fa88de3acd8397b6666afe677161d7404b54809cac8a16069cfd43e	["validate:tokens", "read:users", "read:permissions"]	2025-09-16 07:43:56.743715+00	f	2025-09-15 07:43:56.461329+00	\N
170	1	9ad91c16584b6155ac44c457f537f32ac8046a2c154f7f225a25a05ca60675d0	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-16 07:43:58.292585+00	f	2025-09-15 07:43:57.929128+00	\N
171	3	1bca54fefbaf3404230faec048d89555f6e1c17abdd2e630b957c738fb90dd5a	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 07:44:57.153396+00	f	2025-09-15 07:44:56.87187+00	\N
172	3	af9c4caa5eef1dae5eba05f84d947b0f70587dc0726cad159a2ce3726b55edb5	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 07:58:32.855715+00	f	2025-09-15 07:58:32.571489+00	\N
173	3	0058252a6f89385f7f4702c2e60b21fc92b7ae353d576565ec3d568ec57d9323	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 08:02:59.944531+00	f	2025-09-15 08:02:59.662685+00	\N
174	3	81f692b3f3c38fbcd87c2d1a08b1c268cc2bcbe8dcf22d6a8e58f549cf06174c	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 08:17:16.687783+00	f	2025-09-15 08:17:16.405769+00	\N
175	3	dee310542b28bdd032098f34eb2c84ba0777a7dff79e79d99a19bbd7d887ccee	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 08:18:11.633503+00	f	2025-09-15 08:18:11.352261+00	\N
176	3	117697abec619bd7709adb13beaaae136c289a8310a859cc8076dae9f6a86cef	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 08:19:11.444044+00	f	2025-09-15 08:19:11.162457+00	\N
177	3	0de28c0a98e2fd677fe602f3e0ef75589fcbb6d38762779c890e503e8dccdd8d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 08:57:23.965388+00	f	2025-09-15 08:57:23.683411+00	\N
178	3	4931c046a79c1dc6ca4114c1bacacf94a776b283fa7cff0f168790858c0f9203	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 09:01:08.548405+00	f	2025-09-15 09:01:08.263708+00	\N
179	3	88b5b77b2c9d5aad79eed5edee1c3a561e245d9566138438da415ace15737340	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 09:10:15.36527+00	f	2025-09-15 09:10:15.082944+00	\N
180	3	b65b8748e7501ad51afe2615fd5265fbdc8f722ebd4610894aaf73ece31369c8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 09:24:29.595237+00	f	2025-09-15 09:24:29.313881+00	\N
181	3	aa25a4c6ecaf3e576bb826b860ae7974a71e2bf0a26b6b812c928f7b64cb7963	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 09:41:18.717486+00	f	2025-09-15 09:41:18.433599+00	\N
182	3	0ba50e3712253f1e7761394f16974e1c8f7176848361cd54cbdd5f77aa577f55	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 22:21:32.835412+00	f	2025-09-15 22:21:32.549257+00	\N
183	3	e80dd899f32bb93cd6b3c59a2d6545270e9434fe31a130e07a3ab773a653f60a	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-16 22:24:55.138262+00	f	2025-09-15 22:24:54.855786+00	\N
184	1	1bad25419f56c3540c96531236c1e6bebde6950749adb5afb22d49166c136af2	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-16 22:49:46.794064+00	f	2025-09-15 22:49:46.48864+00	\N
185	2	558206a2826256dea0ca7972e26de6fe24e3a67a8ef465486efd6c55b70efe58	["validate:tokens", "read:users", "read:permissions"]	2025-09-16 22:49:54.351066+00	f	2025-09-15 22:49:54.066438+00	\N
186	3	a72bc1e8722d9f7ac384dff43e8b4ad12b272199c564603c9db9def2384eb72f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-17 05:07:05.135788+00	f	2025-09-16 05:07:04.834777+00	\N
187	2	7b9eff965c5876629a56945a11317637ebb9705c6f00abfb4f26d24e3333e02a	["validate:tokens", "read:users", "read:permissions"]	2025-09-17 05:07:05.555925+00	f	2025-09-16 05:07:05.26274+00	\N
188	1	e6328b700fde857f599f4361aa6ac85f31d3b4b77e37417dd77dc12bea5506b9	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-17 05:07:06.09993+00	f	2025-09-16 05:07:05.803164+00	\N
189	3	f3f2cada8ea0453cf2b6acf457138372c65fe1ae68c7609e704d9a685771b5ff	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 09:00:13.860078+00	f	2025-09-17 09:00:13.572952+00	\N
190	2	7a3b40a821316be0e481e044903aee90cfb10f9b30bbb5c09418e1d4c2fa8953	["validate:tokens", "read:users", "read:permissions"]	2025-09-18 09:00:14.258616+00	f	2025-09-17 09:00:13.97693+00	\N
191	1	21e9588ded51a56251600a599ab872af551b54b1f2ea1659a3d20cf2334a8659	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-18 09:00:15.281015+00	f	2025-09-17 09:00:14.990911+00	\N
192	1	17e09d083df72ad8512704359a0c627e5847e1d68465cbf3cbd706ef70540e96	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-18 09:52:35.854357+00	f	2025-09-17 09:52:35.569669+00	\N
193	3	31cdba847be4b09b9c429834dca5b88b2c35289f51e1b3f7f29b1d5b1d7d942b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 09:52:37.328519+00	f	2025-09-17 09:52:37.041864+00	\N
194	2	67f47e5171e32b6b4ed6dcf0cb2b020c3708461f5e3ed8345d04a97808abc435	["validate:tokens", "read:users", "read:permissions"]	2025-09-18 09:52:37.71455+00	f	2025-09-17 09:52:37.427761+00	\N
195	3	82003102f75ce6353048c17735394a3cca762e9b385951c5bbde0a39b0ae3168	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 10:00:31.799918+00	f	2025-09-17 10:00:31.469734+00	\N
196	2	ece9ad07d4db22a815ff61cd4a1cb8f43fa5651e2ca639d08968f4d13cc523ed	["validate:tokens", "read:users", "read:permissions"]	2025-09-18 10:00:32.275326+00	f	2025-09-17 10:00:31.961444+00	\N
197	1	989496f60a96652e453a2dfb8cde379e76e2b9fadbc81e4d0dc6913e9aaf91de	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-18 10:00:59.532345+00	f	2025-09-17 10:00:59.247612+00	\N
198	3	590370f3cfc67943f78b9802727136130f895b65f60659ae6e1e1f307772a7c3	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 10:02:23.475592+00	f	2025-09-17 10:02:23.149975+00	\N
199	2	e292faa966a1188239b00381d4ea98985a8d3331811b6153d51238f8834c40f9	["validate:tokens", "read:users", "read:permissions"]	2025-09-18 10:02:23.977142+00	f	2025-09-17 10:02:23.647878+00	\N
200	1	b803c06b023b3043abf19f1e7a46a3c6b7bfa21ed4fa2bc4b1e09c06eef40da5	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-18 10:02:26.353231+00	f	2025-09-17 10:02:26.070102+00	\N
201	1	efb438861b73884a80e039aa516085503188f55281aa564496876897d00dd9c4	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-18 22:27:27.010156+00	f	2025-09-17 22:27:26.711795+00	\N
202	2	d16d486d646031a5684f734a705f6a97149745fc6155f74011448a7c1484dcc8	["validate:tokens", "read:users", "read:permissions"]	2025-09-18 22:30:01.232703+00	f	2025-09-17 22:30:00.951535+00	\N
203	3	c4874ebbc02c9f644f50079f5662d3ec4b28b676d4b3ad858a70fd27b3295c74	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 22:31:44.373267+00	f	2025-09-17 22:31:44.092236+00	\N
204	3	8078c497a5dd8101c065dcdba7f67e2c158f9cd4e2e1f06e5e248c00de3e9fb2	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 22:33:59.907494+00	f	2025-09-17 22:33:59.625107+00	\N
205	3	7de99d891e15cb8c2dfee24b1accc27ffe1d3d50023450d1a212323c43ec0ce7	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 22:46:56.33792+00	f	2025-09-17 22:46:56.055473+00	\N
206	3	4fbb0667e8308659094548bb4873672444711274d6df5a58c5cb620384d1942f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 22:49:01.463292+00	f	2025-09-17 22:49:01.181934+00	\N
207	3	3ae3e39f58d1a73cdb06d45f245b21d8bf22f535e824b71441f382cb3f26ed7c	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 22:51:58.090414+00	f	2025-09-17 22:51:57.806708+00	\N
208	3	5d37358c89cd1db7c0f7e2afe4f920ebd011e7bbb3941b3fb8da62747b594dc6	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 22:53:10.546224+00	f	2025-09-17 22:53:10.264519+00	\N
209	3	259288731dc361c19f5aa086423d93a757efd484f95bee4741a27a3c5312186d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-18 22:54:13.964066+00	f	2025-09-17 22:54:13.683041+00	\N
210	1	26760346f8a278a3b72f0e9431990b66e4b124004791e6440dbf483004066723	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 03:20:29.577057+00	f	2025-09-18 03:20:29.289654+00	\N
211	2	9e42cd917e6cae2b039442cd23ed3479a2d641f586cbcf66ac8c05da9d8d4858	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 03:20:39.484559+00	f	2025-09-18 03:20:39.202407+00	\N
212	3	45121bffe4b2e6461b99b8ea0096f253d7cf124f84a71e9442e9c194445407eb	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 04:40:31.135247+00	f	2025-09-18 04:40:30.8435+00	\N
213	2	658a9cd13031e17789ade47dc6e3812757c026f4d01efb2a82eb2321028caf6e	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 04:40:31.542971+00	f	2025-09-18 04:40:31.258497+00	\N
214	1	d20bc1a9b3dbd7c11546a9b233535bc7ae0bdf3242edd1a15738fd48e1e2eefa	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 04:40:32.07453+00	f	2025-09-18 04:40:31.747693+00	\N
215	1	1ed7fb4ddf2c76ff6da2045035725f981a8dd1fbb9f4282b638df8a530cccd9e	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 09:44:48.702764+00	f	2025-09-18 09:44:48.390727+00	\N
216	2	17baba53493d547f4a435e6a574c531619f15b4a21f1b1636bcbbeec2ee49c83	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 09:48:03.591767+00	f	2025-09-18 09:48:03.301659+00	\N
217	3	6edd0f1f0cebe9065dc9be1d920ea07b4812139599f7296762a2f849d092cbc4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 09:55:04.322156+00	f	2025-09-18 09:55:03.96865+00	\N
218	1	d6bbd0e0b9a992c2a71854d7a6cf31974d05fdad42e643557d2992a29b92d64a	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 09:55:04.763395+00	f	2025-09-18 09:55:04.462487+00	\N
219	2	a8159b437555f611046de642765dbf6301bc5d360cb18ffece361fd97695a03d	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 09:55:05.060301+00	f	2025-09-18 09:55:04.771739+00	\N
220	1	f609485d15d45ddcc6df1a5013d65dade29c2cb1efc4e7f98a5368defe1fabd9	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 09:58:13.771991+00	f	2025-09-18 09:58:13.490745+00	\N
221	1	c4b4393c937f973b68c07b62923ee54cc24f6c567ab6caa81f147d6c16fc8eb6	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 10:00:14.454168+00	f	2025-09-18 10:00:14.171266+00	\N
222	1	f25df44ac388544aa5ab17ab3bfdb242aba033702c293aff6b1e73a1d9e94b2f	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 10:00:28.507994+00	f	2025-09-18 10:00:28.22509+00	\N
223	1	b2b5510071ce1492602fba3c37a50f994025a8ea11e8a82d6220641c202ab8f3	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 10:01:38.981501+00	f	2025-09-18 10:01:38.700553+00	\N
224	3	aa4ee7371b1778999297777e5fafb7552833023c159434a08e37b7bf7d1d316e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 10:33:29.734131+00	f	2025-09-18 10:33:29.430876+00	\N
225	2	99cc95e635db43259187c64cbde2502bbdf6f2dd90de5ea5efee37f6c5ef5864	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 10:33:30.057433+00	f	2025-09-18 10:33:29.74227+00	\N
226	1	21d24db225c938a6370ae4ee62e5645a600a45f90328e80d50dc89f0ac19e9ec	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 10:33:30.368567+00	f	2025-09-18 10:33:30.079598+00	\N
227	2	2aea26b95e020d4b8b8018a0d8175f3c769082bf505cbbfbcae3715845ca4209	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 10:33:30.726495+00	f	2025-09-18 10:33:30.382136+00	\N
228	3	cd6c2f97d10252bb3868604c1d0e72db6fcc2f6611d1e66cae8ab454763ad26b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 12:58:15.268534+00	f	2025-09-18 12:58:14.950749+00	\N
229	2	cfcaffe1a4ac1fab79573889c094f0bb9e672b5cee44aaef5bc74ddccdd040e5	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 12:58:15.737321+00	f	2025-09-18 12:58:15.430167+00	\N
230	1	763dc521576f7f9241c809f06b4bb753418b9adac8e5a8962bebb13fe443d677	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 12:58:19.493975+00	f	2025-09-18 12:58:19.185616+00	\N
231	3	faddceccfe579f6bb8299690fff0ec26ca7fb489397086d38b6b61b0cc7e7a79	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 13:12:51.62319+00	f	2025-09-18 13:12:51.289106+00	\N
232	2	3db82e5458d96183c7ddfaf8d08ec8472fc6dddc4d54c3d03b3281ec04659623	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 13:12:52.135619+00	f	2025-09-18 13:12:51.795794+00	\N
233	1	9ca0346b01f44b31e0614cf2f823cd9d645575185481d0217f2cb83485ed23f1	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 13:12:53.774528+00	f	2025-09-18 13:12:53.484928+00	\N
234	2	c7f468fde0597f3adca8cb3db1731ad470245ed273bd03582e33f8accbbc3849	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 13:21:08.55252+00	f	2025-09-18 13:21:08.255414+00	\N
235	3	6c3fa1483f77f1438940d6f955a561450f3ceff323dbc1597f688ad197a0bcd0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 13:21:09.316508+00	f	2025-09-18 13:21:09.032784+00	\N
236	1	f24493b45098752c340d91573a7a6d0d34078416a8c6a5c059cb973667f6330a	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 13:21:10.66328+00	f	2025-09-18 13:21:10.284618+00	\N
237	3	b265f18acb52d8a54c171642c992be950822d7247a61d43d028daf62c57d9243	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 13:24:37.255277+00	f	2025-09-18 13:24:36.96717+00	\N
238	2	a6fd77d048a6bea0560f7bdde3eb4bc538e9d1105f3104c97a73534469877ef4	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 13:24:37.687332+00	f	2025-09-18 13:24:37.391041+00	\N
239	1	63f6a60c7d8b584b8381c0209a9c95ed6161e68a313c2e2bcb8b9a478356e95b	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 13:24:39.162879+00	f	2025-09-18 13:24:38.870976+00	\N
240	2	f6e9ea14015c79c879bdc66adaedab4404871f84d43e0aa397bb1a3fba7bc788	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 13:25:57.318569+00	f	2025-09-18 13:25:57.027152+00	\N
241	3	7df875c966980fcadfa4e3cc44285103af8a1319ca195af7450238770ad7a31e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 13:25:57.66903+00	f	2025-09-18 13:25:57.378452+00	\N
242	1	b2ad26c732bc01ce84eaf7f8c9f6a82e5fdb26ca28088cffb9d0b295ef1647ea	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	2025-09-19 13:25:58.841236+00	f	2025-09-18 13:25:58.542604+00	\N
243	3	35901085953687d0278f8effb51f4067cdee69e3d0b08597826701f75d4a2002	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-19 22:51:02.296464+00	f	2025-09-18 22:51:02.010609+00	\N
244	2	3e1f97158bb2907aeaf20268e5771ee4194ca6bc143f8b0fb6a70bd6d9d80250	["validate:tokens", "read:users", "read:permissions"]	2025-09-19 22:51:02.722119+00	f	2025-09-18 22:51:02.439785+00	\N
245	3	c2936870d85c47ecf904e5d6e0583b43df146b86754616db078b9ae2287a013c	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 02:53:07.15038+00	f	2025-09-19 02:53:06.86798+00	\N
246	3	ff5cb8cc0432489a2785e000352d6e3ccc71ed9d9bba9abbc6a7a900d1410e32	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 03:11:18.297443+00	f	2025-09-19 03:11:17.968445+00	\N
247	2	f1d541d5e4d2e14a346740ced5bcb8983318e21ab8958f71918e9f45c71d6e91	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 03:11:18.737274+00	f	2025-09-19 03:11:18.446063+00	\N
248	4	76f09e73d2a5f6827336f68fa3c73f00c23b16791ce112f7819c7ec5c78678e1	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 03:13:56.138343+00	f	2025-09-19 03:13:55.856605+00	\N
249	4	fadc775a9dadb034e33b537f7c6c2a56b2cab54e9dc042ffb3c790f03b8a76a9	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 03:24:38.980944+00	f	2025-09-19 03:24:38.699286+00	\N
250	4	3aa0339c751f5d3972fbe29a695a097ac041da95d9e29cf4f4d125eca522d922	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 03:25:57.659315+00	f	2025-09-19 03:25:57.377387+00	\N
251	4	ce3733f330a7e216f11b6b6f941bd7ca1eb863d743f6c326790a1e8bbae511da	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 03:31:25.913454+00	f	2025-09-19 03:31:25.630195+00	\N
252	2	127676272abca129e65b5396146a27031d71297f88c7fb2f78d14b0c62fc567c	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 03:31:26.322784+00	f	2025-09-19 03:31:26.017915+00	\N
253	4	f682b34e330fca51cfde09b1688e78c9dc71be0d35141dea56df3c78a63c118b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 03:47:21.461141+00	f	2025-09-19 03:47:21.177501+00	\N
254	4	a41482a4c066288d017966b2526e3c640cbc3d89c84e34c7613866ac861d37b4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 04:42:57.805433+00	f	2025-09-19 04:42:57.523972+00	\N
255	4	eaa61e866c683f48d8ab8ba241b9633db8963484c2e8b36bf224b65dfee1f4b9	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 05:29:03.042416+00	f	2025-09-19 05:29:02.759227+00	\N
256	4	49dab3110b9d975e93793b5212021d79881ba54b5af80054935bdfc3a00beb67	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 05:44:27.452778+00	f	2025-09-19 05:44:27.159424+00	\N
257	4	5989f8e67a0663e27d6641b4b7fc52a20e8a30d8d1f2513903a60746dab9cbc3	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 05:48:47.944583+00	f	2025-09-19 05:48:47.663314+00	\N
258	4	4df76d9bf01977465aec471f7677e67e8dae2411ff889eae456c74cdb1b19337	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 05:53:49.535164+00	f	2025-09-19 05:53:49.247173+00	\N
259	4	3bcfa3dd2c1dfeb51d8b4371d709eeb18599c07fbf8509dc29c4c7fe2f34f35b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 05:55:12.236643+00	f	2025-09-19 05:55:11.952768+00	\N
260	4	29e58466fa4fbbc0e44d2cba5133bd9e15a12a1ff4cfa13686fb711f2e515296	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 05:56:43.304278+00	f	2025-09-19 05:56:43.021693+00	\N
261	4	a90c849379e93bee6fe6872e769e9dbb39933dbcfbd714c16887aa1740c5acb6	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 06:01:14.243559+00	f	2025-09-19 06:01:13.959081+00	\N
262	4	82f90c026dba9a5fa9ccad22bc0d8e5eca670ee57a5c9a26c43171d35a8fbcfe	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 06:05:35.126883+00	f	2025-09-19 06:05:34.84312+00	\N
263	4	66f00f71564ff6fda9d89a09da0c6516860584344b8cbe70316a260c58397528	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 06:25:06.589375+00	f	2025-09-19 06:25:06.305302+00	\N
264	4	861d1f3cf6171a74d261abbd990e2e9c0daa7173a6c017e28d6afb807307064f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 06:39:32.795597+00	f	2025-09-19 06:39:32.511314+00	\N
265	4	fa27beceeb2725c03e0587298b397fd28516f8c9ec1af11e38cc96ae3d4915ed	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 08:40:23.950407+00	f	2025-09-19 08:40:23.663602+00	\N
266	3	0f7410a09cba299194cd06be65752c5b9d6962a81dfe1728811545dbf40e3e15	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 09:29:20.447574+00	f	2025-09-19 09:29:20.113221+00	\N
267	2	66ee1d8307f82bdcdd5726b2adeb06db8fcda2ba70ad40f1c582a39345fc1d07	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 09:29:20.829659+00	f	2025-09-19 09:29:20.492959+00	\N
268	2	2c5d040ccc063804f2c351851481781ac51e7c2d0ace7835a9cb678d73c688de	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 09:31:16.453067+00	f	2025-09-19 09:31:16.155113+00	\N
269	3	d54434da09fa50de4db5869afb7137d95325a6fcb84f8c2f78d68bfec291dfdc	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 09:31:17.254748+00	f	2025-09-19 09:31:16.967296+00	\N
270	3	59ce0d50f0e538c5154ac5121c35e85e9de0d4c8366645ad04e63b53e6705fd3	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 09:37:11.285487+00	f	2025-09-19 09:37:10.988773+00	\N
271	2	7c90051571ef94d6850e5527c03686a7a5e278701b975dcb88210aa03bd03536	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 09:37:11.6766+00	f	2025-09-19 09:37:11.375553+00	\N
272	2	09880dbb9ce0179048732e461c2a5d0f27559457ae4835eab95a392dea02b51c	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 09:37:11.983201+00	f	2025-09-19 09:37:11.688624+00	\N
273	3	c4ab5ea4a93a95f2877fae7136110cee92f27d8ddc9b88fb33538bac7ede0d94	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 09:41:42.539461+00	f	2025-09-19 09:41:42.226+00	\N
274	2	e71d9eb3c419e99f1dca68d6d5c6bcf533b02019909efdac2f4bc6511b4ec4e5	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 09:41:42.972935+00	f	2025-09-19 09:41:42.677353+00	\N
275	3	218c33628d7033e3479c2a2380a7acda22878e6494896af97cbb22193fbfee1a	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 09:46:29.041391+00	f	2025-09-19 09:46:28.711484+00	\N
276	2	633b293c199b05a7ce5a76c5ac1ddd00657d39e6991c087f61a30086b31f76bb	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 09:46:29.46337+00	f	2025-09-19 09:46:29.180542+00	\N
277	3	fcb94771e2ef74df8dec5d44aaf44c965b1337af1064a283d3b059b56e802b3e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 21:28:42.22067+00	f	2025-09-19 21:28:41.928247+00	\N
278	2	0e050318fe8f10ccf0960cfe1fb4bf2459bc72eb97dd199d7b3a2655106849f6	["validate:tokens", "read:users", "read:permissions"]	2025-09-20 21:28:42.619843+00	f	2025-09-19 21:28:42.340493+00	\N
279	4	3502386ae171a2beb93b8d12dc6e0214340705f1dd6132e80d25587256e830ce	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 22:17:34.97227+00	f	2025-09-19 22:17:34.690913+00	\N
280	4	943f4b1c4d71a0a13ccdf7b947a4fd116e2196b29e9fd99e8abbeeba2a170eca	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 22:25:43.079794+00	f	2025-09-19 22:25:42.788467+00	\N
281	4	1c6f0d00aca813384b42485f555a0ebbc812d6575ca571142123583268004c84	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 22:51:51.868071+00	f	2025-09-19 22:51:51.583932+00	\N
282	4	9feffc56df90a5e1fd0daa0fe9ce35b9e432387f5aa05b1d69b21afd28b6ec2d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-20 22:56:31.285956+00	f	2025-09-19 22:56:30.997241+00	\N
283	4	f328628a93df68fed586970cbcf4b2845089dffc4e07369d5aee102482eec880	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:00:47.846235+00	f	2025-09-20 01:00:47.554941+00	\N
284	4	672dafb9f76cd3c1d1284ed01a649f5c356e96c226ae91b3a12e2a1655643ad8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:03:01.87332+00	f	2025-09-20 01:03:01.590812+00	\N
285	4	d5d96996bdb5683369f72ca8b1b92dc9ce854f188dc1e97ceafa5d6578cfdfac	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:05:59.193782+00	f	2025-09-20 01:05:58.89647+00	\N
286	4	06f32bb0708fc8c07d0ab07eac2e65b137eceb8468711728ac92671acc419b84	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:08:45.956695+00	f	2025-09-20 01:08:45.670963+00	\N
287	4	60ee079be4043844539cd8ea498082f04462a4b5bccdfc9d084f57e124c37e51	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:10:30.663574+00	f	2025-09-20 01:10:30.378442+00	\N
288	4	37993b92f873c7725513e4a0c9279cd267da7f23dbe3b267827ec2a86e728696	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:14:04.048996+00	f	2025-09-20 01:14:03.726779+00	\N
289	4	40c7f5efe938c49716bc7366e0dc99b380f4e28027e3ce470bffc466689e1b22	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:16:16.232848+00	f	2025-09-20 01:16:15.946698+00	\N
290	4	6caa56ab57a27ca535a90567337454b8da24307d23c10593eebc22eba7dfdd6f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:27:27.43476+00	f	2025-09-20 01:27:27.146512+00	\N
291	4	f3987f30558d4bdbf41e4ff4ceb041bb0dd5e77816126526b5b7be18e9eaa1b4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 01:30:46.063169+00	f	2025-09-20 01:30:45.779623+00	\N
292	3	f4f2b2479a1476e90c55d70fb6c5a1ad0c466c07e8eaf096acc0f5769296e7ee	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 08:49:54.702243+00	f	2025-09-20 08:49:54.385374+00	\N
293	2	51960614d08e5eebd828d1e43d3b0c8329679735b62c91be69d6038c6def3e47	["validate:tokens", "read:users", "read:permissions"]	2025-09-21 08:49:55.176175+00	f	2025-09-20 08:49:54.889629+00	\N
294	4	62238d5ffaed573ede01a8cc2d06e69c6db72150d4c8ad1336e1d51ed59a9213	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 09:16:49.4895+00	f	2025-09-20 09:16:49.202056+00	\N
295	4	5d0f2787a312cbb83bbb9332bd7c1f4bf28ef95fd87f0e004d2dfc73a6aa2c20	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 09:18:03.948507+00	f	2025-09-20 09:18:03.66688+00	\N
296	4	aebf4ed7e35190f10a2ae9ca3a7daff2d198a5c11c3181c267df35b758c5b07f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 09:23:53.950375+00	f	2025-09-20 09:23:53.663948+00	\N
297	4	f9560089dbdb0ecba61a6a14fa4a05cffebb33148e3fd153146d0700c3496bcd	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 09:26:08.962825+00	f	2025-09-20 09:26:08.677846+00	\N
298	4	ac441183eb81eb1167f14400a8a8748f854a54504471a201a6d755b442e3cb0e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 09:27:37.952848+00	f	2025-09-20 09:27:37.670716+00	\N
299	4	6eb0c719d45ccaff226a3260bb698b7c68930667fd1bc94c7edb787bb8be68db	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 09:30:31.012595+00	f	2025-09-20 09:30:30.728868+00	\N
300	4	0ab5f49256927674753a1d720789b25f9b81315e5fd6583da66c5dce3142c340	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-21 09:32:37.969502+00	f	2025-09-20 09:32:37.686614+00	\N
301	4	a35bad1e3e7a1ff3cb87fb412ad26e6af547b7bf30772f02300f4920b19a95a9	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-22 07:25:02.107323+00	f	2025-09-21 07:25:01.814322+00	\N
302	3	2d037b7f3fcd3738a62f1c89f1696aead1fe9a0aadfca6a546cbee006efc9138	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-26 06:18:17.193346+00	f	2025-09-25 06:18:16.901662+00	\N
303	2	30db692d0f712b5318cc62b6d052ae11eecb4ccc8ba9f8843f20acef7bf714d2	["validate:tokens", "read:users", "read:permissions"]	2025-09-26 06:18:17.594858+00	f	2025-09-25 06:18:17.312011+00	\N
304	4	fc62df17e49f6c5b975bd9c7052027197dd42ad757698e7f13e59b3dfc845052	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-26 23:12:47.211645+00	f	2025-09-25 23:12:46.925016+00	\N
305	4	339b78e0ba2cedffcc0855a3fa46b0bab2f6c7e592347b3ba43a745e80c57fa1	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-09-26 23:15:46.512074+00	f	2025-09-25 23:15:46.226116+00	\N
306	3	b561151bff5185db7ba3bac4c9c53e841c35ba2ee03580db84298189d8d9ac90	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 05:34:29.890616+00	f	2025-09-30 05:34:29.558733+00	\N
307	2	46af378bcf2b275c8b297254fc55c2d3106cb14f348d97b8ea46ad84f6dad443	["validate:tokens", "read:users", "read:permissions"]	2025-10-01 05:34:30.328751+00	f	2025-09-30 05:34:30.033807+00	\N
308	3	eca499713f4e29ba984d68030893e9503337547bda572e206bde54ce001a6000	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 07:12:25.417624+00	f	2025-09-30 07:12:25.113219+00	\N
309	2	c1ac674be97cc87bd46f5567169f9af4b45df78f3c2b328e26f65f56821585aa	["validate:tokens", "read:users", "read:permissions"]	2025-10-01 07:12:25.872455+00	f	2025-09-30 07:12:25.570758+00	\N
310	4	3a30716405f529c8b4a2c1985454d06357c22bd25189a296dc535841789a1998	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 07:16:30.202928+00	f	2025-09-30 07:16:29.917602+00	\N
311	4	b5826cc657178debc67405879ba933f8c3e62145d1bd20252e646d0d52e45676	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 07:58:31.267937+00	f	2025-09-30 07:58:30.963846+00	\N
312	4	4a8624172f1e500e15d175cf16e22a3acb86d0d15f7892812dfdcb2f911cbef1	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 08:04:09.712839+00	f	2025-09-30 08:04:09.429007+00	\N
313	4	b5a11876a38b46e21e5108f5d1a614b2083bd7142b73d11239c4144f666a7b8e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 08:42:00.991905+00	f	2025-09-30 08:42:00.703988+00	\N
314	4	0f7ad4b705853f3a3bbcd75d77f4ec22cd2c21fd6076bbf33c1aa49adb313afe	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 08:55:43.150611+00	f	2025-09-30 08:55:42.864134+00	\N
315	4	0f22352c6a4906a79f92e0d8e21bc550662199474c99adb515a5c7161841c5f0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 08:56:48.019741+00	f	2025-09-30 08:56:47.733971+00	\N
316	4	354bbf3c7ba5343fa175baa64865ed56ad23d4a0a33b2cf32fd50361d758c1df	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 08:57:47.997418+00	f	2025-09-30 08:57:47.713326+00	\N
317	4	4df49009713b0b286d13f9e47427bdd6d93ed1f9b9cd88454e2fc727a542c88e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 08:58:54.375284+00	f	2025-09-30 08:58:54.087731+00	\N
318	4	82b6693ad4ccadcd82f545de21ec73e36c75ec1cb0056eae8b046c5a6cde5b49	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 11:34:15.860743+00	f	2025-09-30 11:34:15.573049+00	\N
319	4	232c7205594efb5def4801f6a0d78f7a7aee9e794cc1fac09ae857f2c612d8bc	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 11:46:58.280857+00	f	2025-09-30 11:46:57.997768+00	\N
320	4	e7193a2502def4053541f4d0ae12272e53468f43a9019387b718f19d702ba3d5	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-01 22:33:26.136695+00	f	2025-09-30 22:33:25.846897+00	\N
321	4	3b175a54009f1e135959ce1ed3f633351699d7f879c7bbfd1a2a827833f85401	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 06:18:59.879258+00	f	2025-10-01 06:18:59.595897+00	\N
322	4	ccf0178ff6884d0b02ea5f45c60f1d976f928e6a432b8eb0b85f412a6f11f6f0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 06:20:09.752466+00	f	2025-10-01 06:20:09.470578+00	\N
323	4	c69f4a822994c86589dc0bf249b61de20358735dbd9726a44e373612d0df247e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 06:21:04.739559+00	f	2025-10-01 06:21:04.458196+00	\N
324	4	7623e7630fdadd744aaedc4e7283acdcf14f4dce25784bca42e939745aa09420	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 06:23:47.087429+00	f	2025-10-01 06:23:46.804442+00	\N
325	3	cb3c3b742f0eaf3d8e9511f3140aa0d286312a2911ea3c44d5ca179aee7d0fb3	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 07:59:44.07017+00	f	2025-10-01 07:59:43.776779+00	\N
326	2	1c4dc5c9d39a201e2e884285f2f1496d6944a63ae65a02db96be566d89d68ef8	["validate:tokens", "read:users", "read:permissions"]	2025-10-02 07:59:44.521139+00	f	2025-10-01 07:59:44.214901+00	\N
327	3	7b34766f1265c0c9017d4ae6da591be19716604c2bf6cec6db8928dee3937211	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 08:01:01.154137+00	f	2025-10-01 08:01:00.862724+00	\N
328	2	8c292cb1d034bfe33293227999f2f6723dc3bcc81cdf191eb83d58226376abb5	["validate:tokens", "read:users", "read:permissions"]	2025-10-02 08:01:01.570502+00	f	2025-10-01 08:01:01.260715+00	\N
329	3	b8a7c19b54dc738213b9b3c0a8611911a06c2469186fe9bdaa57f4c1de943778	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 08:43:35.644269+00	f	2025-10-01 08:43:35.343515+00	\N
330	2	b5766191b73db0b68fdebb72023918fe7d5725562bfc2a4c979a6798eb655779	["validate:tokens", "read:users", "read:permissions"]	2025-10-02 08:43:36.056574+00	f	2025-10-01 08:43:35.767417+00	\N
331	3	125bd85e034b0ccf9479cf801f822b5a8750ef0442b067e5aadf628510221c4f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 08:49:09.516825+00	f	2025-10-01 08:49:09.208381+00	\N
332	2	421174f18e9b794971629888db897e3ec47415680d9fcd125852091ba5c1902d	["validate:tokens", "read:users", "read:permissions"]	2025-10-02 08:49:09.874737+00	f	2025-10-01 08:49:09.578223+00	\N
333	2	a0f453e6b053ef49984817f7bd11d375ba8c296ddcad814449c4814fa359d43d	["validate:tokens", "read:users", "read:permissions"]	2025-10-02 08:49:10.17509+00	f	2025-10-01 08:49:09.883406+00	\N
334	3	3bc4a1e7fe37306f33bd72eb3d33323b991a370bde7125ee8e69d90da094bbf3	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-02 08:50:49.876308+00	f	2025-10-01 08:50:49.569247+00	\N
335	2	f9f6e06b29ef4adc72291cbdfeadc800d0178371b325ae7764f6f148778f854b	["validate:tokens", "read:users", "read:permissions"]	2025-10-02 08:50:50.335601+00	f	2025-10-01 08:50:50.04317+00	\N
336	3	38a0de20c0154ed5108ec0bf5034393f37081f6c361b4e5bf0ac1cb79a0ad17f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-03 06:16:52.811003+00	f	2025-10-02 06:16:52.517722+00	\N
337	2	67e3e24e9bcc7e0441e2e8d0b10be68d75020b73df1407e4daa200265fd8c06a	["validate:tokens", "read:users", "read:permissions"]	2025-10-03 06:16:53.250634+00	f	2025-10-02 06:16:52.956421+00	\N
338	3	8f191ec58747a52da280c4ccc7221ce0d60bd99a032d1e1fc0d1130508cade4e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-03 06:19:10.437558+00	f	2025-10-02 06:19:10.137186+00	\N
339	2	6e0d243172589765c7f03c00ee22f14ff8ab14b1b57a8c98ff4db0de2562c6ec	["validate:tokens", "read:users", "read:permissions"]	2025-10-03 06:19:10.861427+00	f	2025-10-02 06:19:10.571907+00	\N
340	3	6f0aec3121b40dfbcb65535b12a6abe602604a47933265837c6ba4e11b670721	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-03 06:31:14.673411+00	f	2025-10-02 06:31:14.380741+00	\N
341	2	68309cf2626d8ffa9abb4bbd45b0c9a4717fff1f5e36dfc23e13c6ff2f47ceb9	["validate:tokens", "read:users", "read:permissions"]	2025-10-03 06:31:15.181533+00	f	2025-10-02 06:31:14.870084+00	\N
342	3	c682564ca76bf07ebcd4b2bdbbc7df1f9675ddbb2d2f392612ced67fceb4d90b	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-08 10:55:25.255516+00	f	2025-10-07 10:55:24.959288+00	\N
343	2	fc9b3f360d8d32cde5844ab16fb656e764f842584041068e318063a470f8c5b7	["validate:tokens", "read:users", "read:permissions"]	2025-10-08 10:55:25.707773+00	f	2025-10-07 10:55:25.399903+00	\N
344	2	bdebc129b0ac96bf6dc4da3306d00df1128d3a208ec80d77a55e601f27a3bc67	["validate:tokens", "read:users", "read:permissions"]	2025-10-09 07:54:00.534621+00	f	2025-10-08 07:54:00.240997+00	\N
345	3	0b30ae74fa8ee92c03f792ce75f409a3f26d2c681ca9f776761bae66f7a61c4f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 07:57:41.315711+00	f	2025-10-08 07:57:41.007831+00	\N
346	2	e668223571f37c8cbf92bda085a344d33428de05aba3eb5b037a1a8edd14341d	["validate:tokens", "read:users", "read:permissions"]	2025-10-09 07:57:41.760093+00	f	2025-10-08 07:57:41.457689+00	\N
347	3	81a911415e873d27a81df4bd78acb828aee448aa1c4310d9dced7a74aee171b8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 08:00:44.182475+00	f	2025-10-08 08:00:43.883561+00	\N
348	2	5b53796e6fabedc5c317a04f8b417b70a8bc95f27222516cb820a12a788fadf1	["validate:tokens", "read:users", "read:permissions"]	2025-10-09 08:00:44.661207+00	f	2025-10-08 08:00:44.357945+00	\N
349	2	801583cabed5c368d41780c27610b0a4bad37a00570e2e5b3782d8310d5553e0	["validate:tokens", "read:users", "read:permissions"]	2025-10-09 09:24:26.728631+00	f	2025-10-08 09:24:26.43166+00	\N
350	3	2c2a88ffbc97ea8199adc9672e30500efac98b1b9ad72d1c4d2f425c7f253bba	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 09:55:27.696098+00	f	2025-10-08 09:55:27.38707+00	\N
351	2	2fc1ce4de15c009477f3bf3d930fc855eab0347b85a23772955993a45d8adde1	["validate:tokens", "read:users", "read:permissions"]	2025-10-09 09:55:28.122249+00	f	2025-10-08 09:55:27.83826+00	\N
352	3	886692f387fb774dc793eee367b596702c198c06dc40b73e707cc52746d6c701	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 10:05:44.656108+00	f	2025-10-08 10:05:44.361322+00	\N
353	2	0d6555cd2375c06500735b95526ce27c192e4b9244309d411f5b987350e62708	["validate:tokens", "read:users", "read:permissions"]	2025-10-09 10:05:45.081944+00	f	2025-10-08 10:05:44.797387+00	\N
354	4	e8cca2885410d1b2599d22dbf37e9ccc9ce3a0729acb8523ea08a97b8e3faaf5	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 10:21:59.21182+00	f	2025-10-08 10:21:58.923241+00	\N
355	4	ff3250c3cb4f79e0505d4f176435d59430e7599505b7daf68ed54abcde156904	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 10:29:09.838538+00	f	2025-10-08 10:29:09.554822+00	\N
356	4	f57bd3ab82b02f3ec7065901945154da112126f1be6f83ba26a69330f9687925	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 22:17:52.103957+00	f	2025-10-08 22:17:51.806278+00	\N
357	4	537faee2fb0e10734d3eb84e88780a99cdd6d40126e6243007d63fa2bb4e1082	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 22:29:45.901782+00	f	2025-10-08 22:29:45.606713+00	\N
358	4	10ac97fc4641b3c2f1bf5e48e22b5a539b204d06641bfc04b326acd2f79b7c52	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 22:32:53.121104+00	f	2025-10-08 22:32:52.839852+00	\N
359	4	cde919d139cec2f1d0b8ac781f13a4ab02e9f90ce43f6314300171b4c0c063de	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 22:40:25.848149+00	f	2025-10-08 22:40:25.560272+00	\N
360	4	f61d868cf4bd39fad557b8f92f22a9df4f1a14a846f71c4ef6fc4c35ef45f3fe	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 23:11:22.580407+00	f	2025-10-08 23:11:22.295924+00	\N
361	4	1b89633147f729a80a2c5acb73b26d5ca1151ac8ab98d8bfb0e0dd84cd5fa9be	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-09 23:13:20.318566+00	f	2025-10-08 23:13:20.037081+00	\N
362	4	0cc26c7acee9202779e9fb2e8ee2e720373b4dc6a8f87e191303f4ae389ee0c5	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 07:14:04.704527+00	f	2025-10-09 07:14:04.405268+00	\N
363	4	c5525e4e78d1171282911f2aa01cafa32c1cc40f147499577ca9b00a072555ad	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 07:21:44.583723+00	f	2025-10-09 07:21:44.293439+00	\N
364	4	3d88cfc3aed39b53672da217e34a9dcdfc0cafc7b9d3bef5d198fa4a408195bc	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 07:50:39.353586+00	f	2025-10-09 07:50:39.057278+00	\N
365	4	cf4be12faf69cae9db8206f0bc816b3f0f2a81748f91f1e14f2ff22955dfcd38	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 07:57:19.163219+00	f	2025-10-09 07:57:18.875499+00	\N
366	4	0193fb33c004780d64646be533edef16b880a72c295e6666d4f0bcd484f2d261	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 08:13:21.082063+00	f	2025-10-09 08:13:20.781185+00	\N
367	4	f3d04725adb3c372dff2141c2d876b363d23dd02881fdea49ede1ce4aedb100d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 08:15:07.821194+00	f	2025-10-09 08:15:07.540169+00	\N
368	4	9d98ba45cd6614541e5d03039f008390b377092ef91ab9ca46a643b88b0656f9	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 08:41:55.238548+00	f	2025-10-09 08:41:54.956264+00	\N
369	2	b2ecd3b7aa07b0f24b0c9be4fcd00c5862dbb79af8e5b80894f27ae94649692f	["validate:tokens", "read:users", "read:permissions"]	2025-10-10 10:35:17.289326+00	f	2025-10-09 10:35:16.997983+00	\N
370	4	cd8e5034204499edf6bd3daec2b1c3fa6c11e0cd6f584111e4f5d4af92e04d29	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 10:37:01.585594+00	f	2025-10-09 10:37:01.304175+00	\N
371	4	bbf1ffba93243610b8300403ee2fd3eace4c3a492062c868b4509ab31adbc9e9	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 10:44:29.880954+00	f	2025-10-09 10:44:29.597469+00	\N
372	4	ab78d83c09d9df0be9e2b4d0e3d168a0ccc12ef48be28b56ca70908d33e4fbf0	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-10 10:45:37.206772+00	f	2025-10-09 10:45:36.925143+00	\N
373	4	8db3a18a70f26876489f3fa819535db454183e8a7236806751807a69b225e20e	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-11 05:35:03.969503+00	f	2025-10-10 05:35:03.535039+00	\N
374	4	b9ddde47fe5320c3c57067486abed468ddcaf2c8ea9f94836317cc89471346c8	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-11 05:41:26.459452+00	f	2025-10-10 05:41:26.067801+00	\N
375	4	bc399c06d5a0c84406b5bef9545eef20a8b26330b09e2de25fa572a18b3f339f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-11 10:00:58.755844+00	f	2025-10-10 10:00:57.886242+00	\N
376	2	45bab57d5a8b06da0458b7c7873e5272e8c9be41750ef0c37410d20f4e2e746e	["validate:tokens", "read:users", "read:permissions"]	2025-10-11 10:30:42.524492+00	f	2025-10-10 10:30:42.164767+00	\N
377	4	d8abf1ab76d3abcd7ce28045ee7850daa5d6d7a0ca559b8ce5d2b873ae7a2355	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-11 21:10:37.137395+00	f	2025-10-10 21:10:36.830156+00	\N
378	4	1619c839351d71392d626a87d04eb8941d954c0c07ac5c56851d3df5fd685bbd	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-12 03:30:04.510825+00	f	2025-10-11 03:30:04.109541+00	\N
379	4	d53888c5fb1816c5075676d0ba42322771364fb7e26b72cf6fa5946545669325	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-12 03:31:51.562694+00	f	2025-10-11 03:31:51.265861+00	\N
380	4	90f41452a827b0b89448cf56e023ec99b8020a9856403529e61bb2c7dcd3c7ca	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-12 05:43:54.323518+00	f	2025-10-11 05:43:54.009979+00	\N
381	2	e69afc06508271c27fc84077a22869dd8919d0428d54b9d416c0dae7d20defd2	["validate:tokens", "read:users", "read:permissions"]	2025-10-12 12:35:38.457877+00	f	2025-10-11 12:35:38.115799+00	\N
382	4	be1d0404eced2ab7e7556c6ed40eb9b3991efb66b97393b54537faaddc4716ca	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-12 12:50:30.770134+00	f	2025-10-11 12:50:30.326764+00	\N
383	2	4ec9826672ca8b06452f6aeced13cd48421682ce5dc2b18bae0eb2f37cfbd49c	["validate:tokens", "read:users", "read:permissions"]	2025-10-12 12:50:31.658435+00	f	2025-10-11 12:50:31.257218+00	\N
384	4	bf5f0ed32414f3663ecba673ba8c3969e9e611f68c1e70bfb54737309bc67aa4	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-12 22:16:13.099364+00	f	2025-10-11 22:16:12.785926+00	\N
385	4	e9cbf92375419569231adc83d3173559ab602be7570b16bb0d939f4f72c8276d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-12 22:48:32.302366+00	f	2025-10-11 22:48:31.975443+00	\N
386	4	58c7ddb03bee9aea744bafe33fa60d8073679039a53c935476fb02b9c42d6016	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-12 23:06:31.175565+00	f	2025-10-11 23:06:30.850976+00	\N
387	4	9962276c736af53c6b7681798d3c7ff231adb369d784f05ab1d8a23a2e77fc1f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-13 09:41:13.755676+00	f	2025-10-12 09:41:13.285019+00	\N
388	4	e6cc699607cd9a3acb6539368e4544a26421af763a4f1af6882156b4aedfc41d	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-13 09:48:01.088775+00	f	2025-10-12 09:48:00.563053+00	\N
389	4	79f6abbca2eb69b8814d9019b008867c4dbec479f6d38c7d1f9e9fa6f640676f	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-13 10:10:48.782456+00	f	2025-10-12 10:10:48.279899+00	\N
390	4	195d288b9806c5f6030092dd1f0d04e4e1e5af91fd4fae172cbe75f721cc3e97	["validate:tokens", "read:users", "read:permissions", "write:menus"]	2025-10-13 10:20:30.185444+00	f	2025-10-12 10:20:29.353975+00	\N
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.services (id, service_name, service_description, service_secret_hash, allowed_scopes, callback_urls, is_active, created_at, updated_at, last_used) FROM stdin;
3	inventory-service	Inventory Management Service	$2b$12$HZtGmek4N2bKz80hqRgNae8QyJShCXOdsGMyi905XIQhQRHfLV1Aa	["validate:tokens", "read:users", "read:permissions", "write:menus"]	[]	t	2025-09-02 03:58:49.331697+00	2025-10-08 10:05:44.361322+00	2025-10-08 10:05:44.656451+00
2	menu-access-service	Menu & Access Rights Management Service	$2b$12$4rZeqy27DNrWmQa4CTwgoOC1KlBK7dVM3VxOaUl9oDxApp/nMES4G	["validate:tokens", "read:users", "read:permissions"]	[]	t	2025-08-31 04:41:11.54093+00	2025-10-11 12:50:31.257218+00	2025-10-11 12:50:31.658918+00
4	sales-service	sales Management Service	$2b$12$7unipJ5EsWoy8ijOL7gBa.XLepwaJJTJeQhiG5b0MXBMF0j7mN/oq	["validate:tokens", "read:users", "read:permissions", "write:menus"]	[]	t	2025-09-19 03:13:44.131308+00	2025-10-12 10:20:29.353975+00	2025-10-12 10:20:30.18582+00
1	company-partner-service	Company & Partner Management Service	$2b$12$LIr2mjsxSe.RB.22U8llfOIOj0omcxDcaoc6n7doHd4WgKTeZ1f7G	["read:users", "write:users", "read:roles", "write:roles", "read:permissions", "validate:tokens"]	[]	t	2025-08-24 00:58:20.369048+00	2025-09-18 13:25:58.542604+00	2025-09-18 13:25:58.841512+00
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (id, user_id, role_id, assigned_at, assigned_by) FROM stdin;
1	1	1	2025-08-23 04:26:22.146826+00	\N
2	1	6	2025-09-02 07:19:36.523544+00	\N
3	1	8	2025-09-19 04:09:59.265091+00	\N
4	1	9	2025-09-19 04:10:03.613526+00	\N
\.


--
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_sessions (id, user_id, refresh_token, expires_at, created_at, ip_address, user_agent, is_revoked) FROM stdin;
1	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NTkzNDQ1NS45MzYwNDMsImV4cCI6MTc1NjUzOTI1NS45MzYwNDMsIm5iZiI6MTc1NTkzNDQ1NS45MzYwNDN9.WJ3Het-8NQgbhMxeaXmLF2H80__OY0eLwP3p9DvZcPE	2025-08-30 07:34:15.9361+00	2025-08-23 07:34:15.92881+00	\N	\N	f
2	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NTkzNTkwMS4xNTU1NjksImV4cCI6MTc1NjU0MDcwMS4xNTU1NjksIm5iZiI6MTc1NTkzNTkwMS4xNTU1Njl9.GB-R0FtREPJVUti6NMUIBRM_gHp1z3dWe39v27YilEo	2025-08-30 07:58:21.155617+00	2025-08-23 07:58:21.150461+00	\N	\N	f
3	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NTkzNjMyMi43NTA2ODcsImV4cCI6MTc1NjU0MTEyMi43NTA2ODcsIm5iZiI6MTc1NTkzNjMyMi43NTA2ODd9.K7d6Si17CZdLZ9BJVD5JeKoz4oYP5BdfgCmRtzTAt3A	2025-08-30 08:05:22.750734+00	2025-08-23 08:05:22.742607+00	\N	\N	f
4	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NTkzNjM2OC42NDkzMDgsImV4cCI6MTc1NjU0MTE2OC42NDkzMDgsIm5iZiI6MTc1NTkzNjM2OC42NDkzMDh9.GsgYH0kuvorzX7VocZIfQ69JFSbGFLSmGEcwhil3wA0	2025-08-30 08:06:08.649356+00	2025-08-23 08:06:08.646266+00	\N	\N	f
5	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NTk5NzcwNS4xMzMxNTEsImV4cCI6MTc1NjYwMjUwNS4xMzMxNTEsIm5iZiI6MTc1NTk5NzcwNS4xMzMxNTF9.mcayu6c8KBPkBol5B7mhcI-pH0rZ51Hgp2XfCobTHdc	2025-08-31 01:08:25.133201+00	2025-08-24 01:08:25.12084+00	\N	\N	f
6	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NTk5ODY4My40NzMxMjYsImV4cCI6MTc1NjYwMzQ4My40NzMxMjYsIm5iZiI6MTc1NTk5ODY4My40NzMxMjZ9.u3jbH8P3KJsjHTUuh1ZqTAx_mTX0N4tzq_nOPWaMQVo	2025-08-31 01:24:43.473202+00	2025-08-24 01:24:43.466768+00	\N	\N	f
7	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAwMDAwOC4xOTI0MjUsImV4cCI6MTc1NjYwNDgwOC4xOTI0MjUsIm5iZiI6MTc1NjAwMDAwOC4xOTI0MjV9.24zmQmXA-JXTVCh9a5y26L4vQ6JgS6lE57mbnEPNiSg	2025-08-31 01:46:48.192477+00	2025-08-24 01:46:48.180595+00	\N	\N	f
8	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxMzYyNy40NDA3NzUsImV4cCI6MTc1NjYxODQyNy40NDA3NzUsIm5iZiI6MTc1NjAxMzYyNy40NDA3NzV9.mta2oOh9cDNNrGggh5T4qqVsh4c_A7nPiQG0PJJuLvc	2025-08-31 05:33:47.440821+00	2025-08-24 05:33:47.435454+00	\N	\N	f
9	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNTA5MS41ODgyNiwiZXhwIjoxNzU2NjE5ODkxLjU4ODI2LCJuYmYiOjE3NTYwMTUwOTEuNTg4MjZ9.Hd1IwiLhD6X8KjcidlUs1aiW2n4c0dTMmQOpYg6cMVY	2025-08-31 05:58:11.588361+00	2025-08-24 05:58:11.578523+00	\N	\N	f
10	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNTE2NC43Njg1OSwiZXhwIjoxNzU2NjE5OTY0Ljc2ODU5LCJuYmYiOjE3NTYwMTUxNjQuNzY4NTl9.2rQt87D7Cp63F_ieuth3a10hdnOTVH6OtVqkNRdBFik	2025-08-31 05:59:24.768634+00	2025-08-24 05:59:24.765558+00	\N	\N	f
11	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNjU1OS41Njg5MDcsImV4cCI6MTc1NjYyMTM1OS41Njg5MDcsIm5iZiI6MTc1NjAxNjU1OS41Njg5MDd9.SJ4LoaLoOGR_JS4vnMd8wD_x1cgJ2YtsJzOAGoc_EB4	2025-08-31 06:22:39.568959+00	2025-08-24 06:22:39.553645+00	\N	\N	f
12	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNjYwNi42MDQzMjUsImV4cCI6MTc1NjYyMTQwNi42MDQzMjUsIm5iZiI6MTc1NjAxNjYwNi42MDQzMjV9.HgwzbC0IPQy5xGK_j4RDRUotcEje7U3gTyBj-eB-HiQ	2025-08-31 06:23:26.604371+00	2025-08-24 06:23:26.601278+00	\N	\N	f
13	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNjYxNy4zMzMwOSwiZXhwIjoxNzU2NjIxNDE3LjMzMzA5LCJuYmYiOjE3NTYwMTY2MTcuMzMzMDl9.WqmA8McvZ7XU5dKZGwQZNaLdLOm5s6S7anB3f0QUUbQ	2025-08-31 06:23:37.333136+00	2025-08-24 06:23:37.328268+00	\N	\N	f
14	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNjcyMi42Mjc2NTYsImV4cCI6MTc1NjYyMTUyMi42Mjc2NTYsIm5iZiI6MTc1NjAxNjcyMi42Mjc2NTZ9.03rX7eS_vyKLG1o5Y0KU--rTgrOzTm2aN8a6REOQ6gY	2025-08-31 06:25:22.627757+00	2025-08-24 06:25:22.620201+00	\N	\N	f
15	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNjk2OC4wOTAyOSwiZXhwIjoxNzU2NjIxNzY4LjA5MDI5LCJuYmYiOjE3NTYwMTY5NjguMDkwMjl9.mTGbNhixk5x7PedRtb-yORXrSqezHBjTWYG0KWk5vGE	2025-08-31 06:29:28.090337+00	2025-08-24 06:29:28.085006+00	\N	\N	f
16	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxNjk4MC43MzgwNTUsImV4cCI6MTc1NjYyMTc4MC43MzgwNTUsIm5iZiI6MTc1NjAxNjk4MC43MzgwNTV9.nOHa-IdxYPLdDEKmEk07BQbXYF7srYnuONd957bdsqc	2025-08-31 06:29:40.738187+00	2025-08-24 06:29:40.726601+00	\N	\N	f
17	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxODE3My44MzEyOTQsImV4cCI6MTc1NjYyMjk3My44MzEyOTQsIm5iZiI6MTc1NjAxODE3My44MzEyOTR9.CPZpa6_fPmqjYOhAgWa6Gm3sB2jJgZLD4qnvs6-gZgc	2025-08-31 06:49:33.831341+00	2025-08-24 06:49:33.825252+00	\N	\N	f
18	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxOTE1NS4yNjM5NzEsImV4cCI6MTc1NjYyMzk1NS4yNjM5NzEsIm5iZiI6MTc1NjAxOTE1NS4yNjM5NzF9.i1jvflPVdZ3DLydcnQ9t8CctXwSmDyxpzDjrMgTb790	2025-08-31 07:05:55.264019+00	2025-08-24 07:05:55.256862+00	\N	\N	f
19	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxOTE2My42MDk5NTQsImV4cCI6MTc1NjYyMzk2My42MDk5NTQsIm5iZiI6MTc1NjAxOTE2My42MDk5NTR9.XxXXgzspfbZVKZmdcHZPzzCePd0CrNKP1VS030ab68k	2025-08-31 07:06:03.610128+00	2025-08-24 07:06:03.603531+00	\N	\N	f
20	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAxOTY1NC45MTgyODksImV4cCI6MTc1NjYyNDQ1NC45MTgyODksIm5iZiI6MTc1NjAxOTY1NC45MTgyODl9.QZHp_eXdgTobYy2dAgTM1Jjab0C0riryg6jKSfbhckk	2025-08-31 07:14:14.91834+00	2025-08-24 07:14:14.912091+00	\N	\N	f
21	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjAyODg2My4zNTg3NjYsImV4cCI6MTc1NjYzMzY2My4zNTg3NjYsIm5iZiI6MTc1NjAyODg2My4zNTg3NjZ9.f78cuKbRTafBwAZ6-tjG7cz-31oqBvszIcWPf87Mhzk	2025-08-31 09:47:43.358843+00	2025-08-24 09:47:43.350656+00	\N	\N	f
22	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjA3NTM3Ni45ODgwMTgsImV4cCI6MTc1NjY4MDE3Ni45ODgwMTgsIm5iZiI6MTc1NjA3NTM3Ni45ODgwMTh9.tPRJG24KY4WvU_dFG5VloJviBjD7HGTpCSarxGI7pqI	2025-08-31 22:42:56.988068+00	2025-08-24 22:42:56.982362+00	\N	\N	f
23	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjA3NTYyMS43MjAxMDgsImV4cCI6MTc1NjY4MDQyMS43MjAxMDgsIm5iZiI6MTc1NjA3NTYyMS43MjAxMDh9.RQmG5rmMexjOC00nNmFRG8qKpUp6UzIdOr454DrMhjM	2025-08-31 22:47:01.720151+00	2025-08-24 22:47:01.717008+00	\N	\N	f
24	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjA3NjYwMi41ODM0OTQsImV4cCI6MTc1NjY4MTQwMi41ODM0OTQsIm5iZiI6MTc1NjA3NjYwMi41ODM0OTR9.VVzcTdWEkhfT5RE8ysreOBdiDJMYTTiGeySPukFYR2o	2025-08-31 23:03:22.583541+00	2025-08-24 23:03:22.571236+00	\N	\N	f
25	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjA3NjcyNi41OTAwMjMsImV4cCI6MTc1NjY4MTUyNi41OTAwMjMsIm5iZiI6MTc1NjA3NjcyNi41OTAwMjN9.QVG0MDaJnsVldgBH3HdU2Y6aTo2h7v0aocgx0K0Q_MM	2025-08-31 23:05:26.590072+00	2025-08-24 23:05:26.5867+00	\N	\N	f
26	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjA3NzUyMS42MDMyMzksImV4cCI6MTc1NjY4MjMyMS42MDMyMzksIm5iZiI6MTc1NjA3NzUyMS42MDMyMzl9.l1W87PFEv_ETRlyjZHqO7HVXEyVopWj5yOsfSUNTuwU	2025-08-31 23:18:41.603284+00	2025-08-24 23:18:41.598079+00	\N	\N	f
27	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjA4NjA5My40NjY5MSwiZXhwIjoxNzU2NjkwODkzLjQ2NjkxLCJuYmYiOjE3NTYwODYwOTMuNDY2OTF9.Xc82xa8AdJgMANVJpBjaDD0T5jU2abGRaal_RqgCH5M	2025-09-01 01:41:33.466958+00	2025-08-25 01:41:33.460101+00	\N	\N	f
28	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjA5MDk3NS45NjYwMjMsImV4cCI6MTc1NjY5NTc3NS45NjYwMjMsIm5iZiI6MTc1NjA5MDk3NS45NjYwMjN9.wxxNsBRALUOD-ifSRXaRERvmEPp7Uj868yE-Kg8X_mo	2025-09-01 03:02:55.96607+00	2025-08-25 03:02:55.960451+00	\N	\N	f
29	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjEwODM5My4wMjI2NDQsImV4cCI6MTc1NjcxMzE5My4wMjI2NDQsIm5iZiI6MTc1NjEwODM5My4wMjI2NDR9.zYNzo3XNayfdLuykPG677XD8jysHZXooZKfDstvRSdE	2025-09-01 07:53:13.022719+00	2025-08-25 07:53:13.016602+00	\N	\N	f
30	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjExMDU4Mi42NDQ5OTYsImV4cCI6MTc1NjcxNTM4Mi42NDQ5OTYsIm5iZiI6MTc1NjExMDU4Mi42NDQ5OTZ9.tONkf2H3G-F70WCDNr5JA-2t4uF0BjebdM70TVK4oEc	2025-09-01 08:29:42.645043+00	2025-08-25 08:29:42.639683+00	\N	\N	f
31	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjExMDk1MC4xOTcwOTIsImV4cCI6MTc1NjcxNTc1MC4xOTcwOTIsIm5iZiI6MTc1NjExMDk1MC4xOTcwOTJ9.RHzCFLpnof1lNldiyHYglbKDb0AaTBXwqX8ps4v7XwA	2025-09-01 08:35:50.197139+00	2025-08-25 08:35:50.184986+00	\N	\N	f
32	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjExNzM4MC45MDY2MDEsImV4cCI6MTc1NjcyMjE4MC45MDY2MDEsIm5iZiI6MTc1NjExNzM4MC45MDY2MDF9.9gEFZECAwbY8xPFOAjOh-dqyHwkSl25amfEHdfL6eNQ	2025-09-01 10:23:00.906713+00	2025-08-25 10:23:00.899003+00	\N	\N	f
33	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjE2MjQ3Ni4zMTk2ODUsImV4cCI6MTc1Njc2NzI3Ni4zMTk2ODUsIm5iZiI6MTc1NjE2MjQ3Ni4zMTk2ODV9.BRm5AQUTDgpehNzVu883B8VUYoZGwYd_7-s3YJbHrYI	2025-09-01 22:54:36.319731+00	2025-08-25 22:54:36.314542+00	\N	\N	f
34	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjU2MzM4Ny41ODg2OTUsImV4cCI6MTc1NzE2ODE4Ny41ODg2OTUsIm5iZiI6MTc1NjU2MzM4Ny41ODg2OTV9.HmGut4er4Erg_9ver1tKSbQFBqqn6ZBy8Rv11xzIzk0	2025-09-06 14:16:27.588748+00	2025-08-30 14:16:27.576605+00	\N	\N	f
35	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjU2NDcyMy43NzY1NjMsImV4cCI6MTc1NzE2OTUyMy43NzY1NjMsIm5iZiI6MTc1NjU2NDcyMy43NzY1NjN9.EZdgC9G9onpx3miNqRz9xhllRGgOyNi18VDBdZ9jsvg	2025-09-06 14:38:43.776644+00	2025-08-30 14:38:43.770704+00	\N	\N	f
36	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjU2NTY2NS40NTg5OTcsImV4cCI6MTc1NzE3MDQ2NS40NTg5OTcsIm5iZiI6MTc1NjU2NTY2NS40NTg5OTd9.QBMyyykTfwXo9AQvMebZI1p8sXC0F89056z4yYWrZWg	2025-09-06 14:54:25.459042+00	2025-08-30 14:54:25.453556+00	\N	\N	f
37	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwMDAzNS4xMTg2NDUsImV4cCI6MTc1NzIwNDgzNS4xMTg2NDUsIm5iZiI6MTc1NjYwMDAzNS4xMTg2NDV9.3YYWlrbCJ1vhMmf9Q7kYk-WvggYpMuvioXmPAHsqbzU	2025-09-07 00:27:15.118699+00	2025-08-31 00:27:15.090884+00	\N	\N	f
38	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwMjI1Mi40NTY0NDIsImV4cCI6MTc1NzIwNzA1Mi40NTY0NDIsIm5iZiI6MTc1NjYwMjI1Mi40NTY0NDJ9.WFSthfZlzJjBFN7qfB9GY-TnU0VWOsfJIPgSU0V4CVI	2025-09-07 01:04:12.456501+00	2025-08-31 01:04:12.445967+00	\N	\N	f
39	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwNDk1OC4wNjM1MjcsImV4cCI6MTc1NzIwOTc1OC4wNjM1MjcsIm5iZiI6MTc1NjYwNDk1OC4wNjM1Mjd9.dqDKRXBYp79RnQgho2Rwt6ri3wA2m9ckFiceBv8TYNM	2025-09-07 01:49:18.063575+00	2025-08-31 01:49:18.057446+00	\N	\N	f
40	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwNTkyNi44MDI1MjksImV4cCI6MTc1NzIxMDcyNi44MDI1MjksIm5iZiI6MTc1NjYwNTkyNi44MDI1Mjl9.RUEFPXUyX616SLFWMh9aqdrmvdptxP_B_0FwGs_lxu0	2025-09-07 02:05:26.802588+00	2025-08-31 02:05:26.796754+00	\N	\N	f
41	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwNjc1NC45ODIyNjIsImV4cCI6MTc1NzIxMTU1NC45ODIyNjIsIm5iZiI6MTc1NjYwNjc1NC45ODIyNjJ9.RbGTQBMFL56nhVc-tO5VK2EaznhqTUfd6-EKrW5jk6c	2025-09-07 02:19:14.982306+00	2025-08-31 02:19:14.976918+00	\N	\N	f
42	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwNzQ5OS41MTU4MTEsImV4cCI6MTc1NzIxMjI5OS41MTU4MTEsIm5iZiI6MTc1NjYwNzQ5OS41MTU4MTF9._orMhSXMhiHIrPdH1e6DBDoaHgxtnKB6uM_C2mypFJ4	2025-09-07 02:31:39.515857+00	2025-08-31 02:31:39.510169+00	\N	\N	f
43	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwNzg1MS42NTY0NDIsImV4cCI6MTc1NzIxMjY1MS42NTY0NDIsIm5iZiI6MTc1NjYwNzg1MS42NTY0NDJ9.n0ZRQS_Ljjud_Oe7TZt_LqshQuj_boP9FGdAY-nrlUI	2025-09-07 02:37:31.656492+00	2025-08-31 02:37:31.651151+00	\N	\N	f
44	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwNzg2Ny4wNDI2OTIsImV4cCI6MTc1NzIxMjY2Ny4wNDI2OTIsIm5iZiI6MTc1NjYwNzg2Ny4wNDI2OTJ9.3QykTQLtAQklyBbDR1mgVKs6RLX3fPpmYtToKjF5TLY	2025-09-07 02:37:47.042737+00	2025-08-31 02:37:47.03966+00	\N	\N	f
45	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwODAwNy4xMjc4MTEsImV4cCI6MTc1NzIxMjgwNy4xMjc4MTEsIm5iZiI6MTc1NjYwODAwNy4xMjc4MTF9.S7M3b4INUfANhO2vYHjptG7e_5YDausbcMWEj_t2vUQ	2025-09-07 02:40:07.127858+00	2025-08-31 02:40:07.124712+00	\N	\N	f
46	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwODM4OC41Mzc5NDQsImV4cCI6MTc1NzIxMzE4OC41Mzc5NDQsIm5iZiI6MTc1NjYwODM4OC41Mzc5NDR9.6dWu_L4IuSa3YPQlYgQ87uIiknPhwU9H8Gb2R3Nu0XI	2025-09-07 02:46:28.537989+00	2025-08-31 02:46:28.532954+00	\N	\N	f
47	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwODk5Ny4xNTY5LCJleHAiOjE3NTcyMTM3OTcuMTU2OSwibmJmIjoxNzU2NjA4OTk3LjE1Njl9.-h8NNrqHbn9T5GUdGG7a3RZujzI6zkvi1vcMDDM18tA	2025-09-07 02:56:37.156966+00	2025-08-31 02:56:37.148731+00	\N	\N	f
48	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYwOTY5MC43NDQwMzksImV4cCI6MTc1NzIxNDQ5MC43NDQwMzksIm5iZiI6MTc1NjYwOTY5MC43NDQwMzl9.jwl66w9dCeI3K7eEmIa4ygET_T8DoqrpYmwgxI7gZhk	2025-09-07 03:08:10.74412+00	2025-08-31 03:08:10.730464+00	\N	\N	f
49	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxMjY1OS42MDU1MzQsImV4cCI6MTc1NzIxNzQ1OS42MDU1MzQsIm5iZiI6MTc1NjYxMjY1OS42MDU1MzR9.hHAxotPCaw4dy78W9J8JOyqhtFvQRN6oMbvpp0MqLfk	2025-09-07 03:57:39.605579+00	2025-08-31 03:57:39.600091+00	\N	\N	f
50	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxMzY2NC40MDE0LCJleHAiOjE3NTcyMTg0NjQuNDAxNCwibmJmIjoxNzU2NjEzNjY0LjQwMTR9.sLpbCZdjM7GhEC4cazSmxR8O3WiYDBbiTB0q2Bq-5jk	2025-09-07 04:14:24.401466+00	2025-08-31 04:14:24.395552+00	\N	\N	f
51	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxMzc2NS4yNDI2MTYsImV4cCI6MTc1NzIxODU2NS4yNDI2MTYsIm5iZiI6MTc1NjYxMzc2NS4yNDI2MTZ9.5bvdqPPymexHoqcf9aJknuAY3e53fKIsJfvafXZaFJM	2025-09-07 04:16:05.24266+00	2025-08-31 04:16:05.239349+00	\N	\N	f
52	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxNTIyNS4xMTM5NTgsImV4cCI6MTc1NzIyMDAyNS4xMTM5NTgsIm5iZiI6MTc1NjYxNTIyNS4xMTM5NTh9.cV1pbpDDdo86Q3CRuw0PpqQatryQknqLH6S8bERFiuY	2025-09-07 04:40:25.114044+00	2025-08-31 04:40:25.094532+00	\N	\N	f
53	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxNTg4My45Nzk2MTcsImV4cCI6MTc1NzIyMDY4My45Nzk2MTcsIm5iZiI6MTc1NjYxNTg4My45Nzk2MTd9.AyeVQSnM0sak-woVLlU14Tkg_00N9FpY7gwcqjyBqSY	2025-09-07 04:51:23.979713+00	2025-08-31 04:51:23.96401+00	\N	\N	f
54	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxNjgwMC44NTMzMDEsImV4cCI6MTc1NzIyMTYwMC44NTMzMDEsIm5iZiI6MTc1NjYxNjgwMC44NTMzMDF9.sQnXDFIthxi0k1axhNVy9oUcQVlY1CXZg4OmytxMiaQ	2025-09-07 05:06:40.853352+00	2025-08-31 05:06:40.847739+00	\N	\N	f
55	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxNzcyNy4wNDQ5NDUsImV4cCI6MTc1NzIyMjUyNy4wNDQ5NDUsIm5iZiI6MTc1NjYxNzcyNy4wNDQ5NDV9.z9z06J1tmpSOmtr9w8LmniVO2PtazAUNv4_f6pt-7NY	2025-09-07 05:22:07.044992+00	2025-08-31 05:22:07.037638+00	\N	\N	f
56	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxODMyOC4yOTU3NiwiZXhwIjoxNzU3MjIzMTI4LjI5NTc2LCJuYmYiOjE3NTY2MTgzMjguMjk1NzZ9.tSjX9k0pcm2d8j2rbZdCY5iTercF2SAI0NPbMgVIuv8	2025-09-07 05:32:08.295811+00	2025-08-31 05:32:08.289174+00	\N	\N	f
57	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxODkyNi4xMzU2NSwiZXhwIjoxNzU3MjIzNzI2LjEzNTY1LCJuYmYiOjE3NTY2MTg5MjYuMTM1NjV9.hK7WiL6Ngi8frRsFI84to5H9lpUkAwOjlcJhMlWhgjc	2025-09-07 05:42:06.135696+00	2025-08-31 05:42:06.126507+00	\N	\N	f
58	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxOTk2My42NzUxMzgsImV4cCI6MTc1NzIyNDc2My42NzUxMzgsIm5iZiI6MTc1NjYxOTk2My42NzUxMzh9.clnDYk-z5EtbrT5Y2YmNCEjwFKSu4SJPJGVC5tE-0UE	2025-09-07 05:59:23.675187+00	2025-08-31 05:59:23.668633+00	\N	\N	f
59	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYxOTk3NS44NTczMTQsImV4cCI6MTc1NzIyNDc3NS44NTczMTQsIm5iZiI6MTc1NjYxOTk3NS44NTczMTR9.esaW05xlTaSYyJ9oWOsLq8MclDMJkLNJ6fzYg470ndo	2025-09-07 05:59:35.857363+00	2025-08-31 05:59:35.854236+00	\N	\N	f
60	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyMDgzNy45MjgzNzMsImV4cCI6MTc1NzIyNTYzNy45MjgzNzMsIm5iZiI6MTc1NjYyMDgzNy45MjgzNzN9.Z9y39qeUfTIMY9mt8Q0mdgN_ee0A6kLPTsVd3YP8Sy4	2025-09-07 06:13:57.928419+00	2025-08-31 06:13:57.922694+00	\N	\N	f
61	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyMDkwMi4yMDMwMjIsImV4cCI6MTc1NzIyNTcwMi4yMDMwMjIsIm5iZiI6MTc1NjYyMDkwMi4yMDMwMjJ9.v7khsPsXg0ZzdIJkbhLs3J_WUmIjnRYqMCNdXezVMA0	2025-09-07 06:15:02.203079+00	2025-08-31 06:15:02.199773+00	\N	\N	f
62	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyMjI1MS42MDUzMDMsImV4cCI6MTc1NzIyNzA1MS42MDUzMDMsIm5iZiI6MTc1NjYyMjI1MS42MDUzMDN9.tR6DO9H5ZZ_Q1k_GErhixAqIXdb1ByxbYkmlXE-5Ckc	2025-09-07 06:37:31.605353+00	2025-08-31 06:37:31.599319+00	\N	\N	f
63	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNTI4OC42ODUyMjYsImV4cCI6MTc1NzIzMDA4OC42ODUyMjYsIm5iZiI6MTc1NjYyNTI4OC42ODUyMjZ9.ulkYrKz4gEgpYv36UoyGirU2FwVilhYpxg22eA3IgcE	2025-09-07 07:28:08.685272+00	2025-08-31 07:28:08.675664+00	\N	\N	f
64	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNTQzMC4zMTIzMjcsImV4cCI6MTc1NzIzMDIzMC4zMTIzMjcsIm5iZiI6MTc1NjYyNTQzMC4zMTIzMjd9.UzpWbvLNNiZU8SOc4VPEln8V5HfM7YnLL1EcAcJ8KSg	2025-09-07 07:30:30.312372+00	2025-08-31 07:30:30.309204+00	\N	\N	f
65	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNTQ3MS43NjE3MTEsImV4cCI6MTc1NzIzMDI3MS43NjE3MTEsIm5iZiI6MTc1NjYyNTQ3MS43NjE3MTF9.0I3ca013DwT_ZYexvMjZOub-Ki--P2oATRuutwxTHbQ	2025-09-07 07:31:11.761786+00	2025-08-31 07:31:11.754861+00	\N	\N	f
66	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNTUyMy4wMTUxMTUsImV4cCI6MTc1NzIzMDMyMy4wMTUxMTUsIm5iZiI6MTc1NjYyNTUyMy4wMTUxMTV9.0XoJzi20_xMMHDLuia3_aqNt2SgQH4E80T5_xtEiMg0	2025-09-07 07:32:03.015179+00	2025-08-31 07:32:03.012277+00	\N	\N	f
67	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNTYzMC4xNTk1NjUsImV4cCI6MTc1NzIzMDQzMC4xNTk1NjUsIm5iZiI6MTc1NjYyNTYzMC4xNTk1NjV9.9of76n1qv5mRD0-eAEcEheC3B-22H2CRIiEgxAKOl3c	2025-09-07 07:33:50.159615+00	2025-08-31 07:33:50.156259+00	\N	\N	f
68	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNjc1OC42NDkyNjcsImV4cCI6MTc1NzIzMTU1OC42NDkyNjcsIm5iZiI6MTc1NjYyNjc1OC42NDkyNjd9.7StqL81D2nUUVnAqaR8bGs2eCeDRFsD5Sn2tsdL4URA	2025-09-07 07:52:38.649373+00	2025-08-31 07:52:38.640198+00	\N	\N	f
69	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNjk3My41NjM0MzksImV4cCI6MTc1NzIzMTc3My41NjM0MzksIm5iZiI6MTc1NjYyNjk3My41NjM0Mzl9.mhn_B4f6LFdsafRQocy2-Coh75tU06RVAVALdKCZIH0	2025-09-07 07:56:13.563483+00	2025-08-31 07:56:13.560359+00	\N	\N	f
70	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNzAwMC4yODU3MzUsImV4cCI6MTc1NzIzMTgwMC4yODU3MzUsIm5iZiI6MTc1NjYyNzAwMC4yODU3MzV9.-EKpqcQO457VIICMnP62AWZ16tDXM14NFzg3TD5ekcI	2025-09-07 07:56:40.285784+00	2025-08-31 07:56:40.282792+00	\N	\N	f
71	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyNzUxMi45Njk0NDMsImV4cCI6MTc1NzIzMjMxMi45Njk0NDMsIm5iZiI6MTc1NjYyNzUxMi45Njk0NDN9._devl-sXBP8SZBwCz70TN3KeCyp6FH7VuP4wQns8tEg	2025-09-07 08:05:12.969542+00	2025-08-31 08:05:12.955458+00	\N	\N	f
72	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYyODA2OS40NDEyNzYsImV4cCI6MTc1NzIzMjg2OS40NDEyNzYsIm5iZiI6MTc1NjYyODA2OS40NDEyNzZ9.mzoMQ7BMdJFIF2GpP3kdTMHf8luW1cGzeo_fCbcZqXU	2025-09-07 08:14:29.441325+00	2025-08-31 08:14:29.435417+00	\N	\N	f
73	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYzMDU3NC45ODAxOTUsImV4cCI6MTc1NzIzNTM3NC45ODAxOTUsIm5iZiI6MTc1NjYzMDU3NC45ODAxOTV9.kRH3RsdJ9Nktl1AxoXdolxCZ2jJaldeOLven0MVVOEU	2025-09-07 08:56:14.98024+00	2025-08-31 08:56:14.975129+00	\N	\N	f
74	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYzMDcxMy4zOTI1MjQsImV4cCI6MTc1NzIzNTUxMy4zOTI1MjQsIm5iZiI6MTc1NjYzMDcxMy4zOTI1MjR9.VnFfyf8XufkjekDT6h8nog6CfrApTHQAvcH3jnSvc_4	2025-09-07 08:58:33.392572+00	2025-08-31 08:58:33.389563+00	\N	\N	f
75	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYzMDcyNC43NzA1MzUsImV4cCI6MTc1NzIzNTUyNC43NzA1MzUsIm5iZiI6MTc1NjYzMDcyNC43NzA1MzV9.8NQ0ME0VAS0r7nMsI9zMFMpSVraGKJGTvIQ-4bsJ_m0	2025-09-07 08:58:44.770585+00	2025-08-31 08:58:44.76747+00	\N	\N	f
76	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYzMDgwOC41NTkzOTcsImV4cCI6MTc1NzIzNTYwOC41NTkzOTcsIm5iZiI6MTc1NjYzMDgwOC41NTkzOTd9.4_M7zHQUJLGxnKotCnAJg8Zij-6qUuwPNDCt5VdfjUc	2025-09-07 09:00:08.559445+00	2025-08-31 09:00:08.555631+00	\N	\N	f
77	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYzMDk1OC40MzM2NzcsImV4cCI6MTc1NzIzNTc1OC40MzM2NzcsIm5iZiI6MTc1NjYzMDk1OC40MzM2Nzd9.TMfuvi6PNNOC-rUKGirl5IdJsdldW4-RS1RGkeIZdss	2025-09-07 09:02:38.433765+00	2025-08-31 09:02:38.417164+00	\N	\N	f
78	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjYzMjMwNC4yMzk0OTMsImV4cCI6MTc1NzIzNzEwNC4yMzk0OTMsIm5iZiI6MTc1NjYzMjMwNC4yMzk0OTN9.qo-kcRBsDkqBVC4lowS5FLjhTiV_q1_1jLyIxUm2gME	2025-09-07 09:25:04.239574+00	2025-08-31 09:25:04.233339+00	\N	\N	f
79	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY0ODcyMS4wOTg3NDgsImV4cCI6MTc1NzI1MzUyMS4wOTg3NDgsIm5iZiI6MTc1NjY0ODcyMS4wOTg3NDh9.cyERMvlziMjpLqptdGjUSbbvgPa26PNgzwcXEy83ZbU	2025-09-07 13:58:41.098807+00	2025-08-31 13:58:41.092943+00	\N	\N	f
80	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY0OTkxMi41OTg2MjUsImV4cCI6MTc1NzI1NDcxMi41OTg2MjUsIm5iZiI6MTc1NjY0OTkxMi41OTg2MjV9.kb2no8KNBL0CFPrHnCGf-PQeYulbJcR0Vq2YbqUgGmM	2025-09-07 14:18:32.598676+00	2025-08-31 14:18:32.593552+00	\N	\N	f
81	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY3OTMwNy4zNTU5NzIsImV4cCI6MTc1NzI4NDEwNy4zNTU5NzIsIm5iZiI6MTc1NjY3OTMwNy4zNTU5NzJ9.WhfpycJEj1h0ZLdnOmPGSWgmP55sVqPhJ227uYq1gJ0	2025-09-07 22:28:27.356016+00	2025-08-31 22:28:27.349969+00	\N	\N	f
82	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY4MDIyMC44NzYzMDgsImV4cCI6MTc1NzI4NTAyMC44NzYzMDgsIm5iZiI6MTc1NjY4MDIyMC44NzYzMDh9.xu4ySOybmFFhgAetdW0OmE9WoQKrJKeCIVo9lkTo_60	2025-09-07 22:43:40.876358+00	2025-08-31 22:43:40.870914+00	\N	\N	f
83	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY4MTQxNS43NjIyNDIsImV4cCI6MTc1NzI4NjIxNS43NjIyNDIsIm5iZiI6MTc1NjY4MTQxNS43NjIyNDJ9.gdhbmo1Q-kTc62lKwiju9QYTCWqJFMUFAuPrW3hVuTU	2025-09-07 23:03:35.762293+00	2025-08-31 23:03:35.756487+00	\N	\N	f
84	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY5NDk4OC43Nzk4MDYsImV4cCI6MTc1NzI5OTc4OC43Nzk4MDYsIm5iZiI6MTc1NjY5NDk4OC43Nzk4MDZ9.o3frfc1W-lH2a3EGR1PDtDzuIf6z59rNN4x0IcbRz1w	2025-09-08 02:49:48.779853+00	2025-09-01 02:49:48.773933+00	\N	\N	f
85	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY5NTk3NC43MDk3MTgsImV4cCI6MTc1NzMwMDc3NC43MDk3MTgsIm5iZiI6MTc1NjY5NTk3NC43MDk3MTh9.oDPhA3ZjzRggUshOoBBmPy1VYnrBCzIWMypCXw2ukoQ	2025-09-08 03:06:14.709762+00	2025-09-01 03:06:14.704665+00	\N	\N	f
86	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY5ODcyMy4xODI0NjIsImV4cCI6MTc1NzMwMzUyMy4xODI0NjIsIm5iZiI6MTc1NjY5ODcyMy4xODI0NjJ9.ZHepk3a-HuvM6eVa_96Kp_CEVd5LreEgGa4d5Dli_nU	2025-09-08 03:52:03.182515+00	2025-09-01 03:52:03.176136+00	\N	\N	f
87	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjY5OTg4MS43Mjk3ODgsImV4cCI6MTc1NzMwNDY4MS43Mjk3ODgsIm5iZiI6MTc1NjY5OTg4MS43Mjk3ODh9.jCz3fRkInfE2Ta53fxXnPxTo2OmIVtBICVxUjEUpdq4	2025-09-08 04:11:21.729833+00	2025-09-01 04:11:21.72418+00	\N	\N	f
88	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcwNTAyOS4zOTg2NjgsImV4cCI6MTc1NzMwOTgyOS4zOTg2NjgsIm5iZiI6MTc1NjcwNTAyOS4zOTg2Njh9.LQYZlLcnY6yFjnBy0lJrraoVZFQAwu9t4sjUDOm8Slw	2025-09-08 05:37:09.398737+00	2025-09-01 05:37:09.387677+00	\N	\N	f
89	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcwNzQxNi45OTM0MDMsImV4cCI6MTc1NzMxMjIxNi45OTM0MDMsIm5iZiI6MTc1NjcwNzQxNi45OTM0MDN9.hJFuEMRI19dxoxwkU4ua11u2-UnxukW1XF_AVovvr44	2025-09-08 06:16:56.993482+00	2025-09-01 06:16:56.982218+00	\N	\N	f
90	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcwOTY0Ni4xMTEzNDIsImV4cCI6MTc1NzMxNDQ0Ni4xMTEzNDIsIm5iZiI6MTc1NjcwOTY0Ni4xMTEzNDJ9.lbdd09WHFa2K-YL23EnschwWR0xL3525UzkLFMWxpmU	2025-09-08 06:54:06.111389+00	2025-09-01 06:54:06.103446+00	\N	\N	f
91	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxNDcxOC45NjI5ODcsImV4cCI6MTc1NzMxOTUxOC45NjI5ODcsIm5iZiI6MTc1NjcxNDcxOC45NjI5ODd9.wWjkh-JfWbKhbqYjKP0rbsgZ1ttX_uc5jMDd9E-7pjg	2025-09-08 08:18:38.963051+00	2025-09-01 08:18:38.956195+00	\N	\N	f
92	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxNTcxMS45ODM0MTksImV4cCI6MTc1NzMyMDUxMS45ODM0MTksIm5iZiI6MTc1NjcxNTcxMS45ODM0MTl9.P9qVu6Do-0LUXTrkycvwpJTUrU9a-4yfSTfN8GxPCTk	2025-09-08 08:35:11.983464+00	2025-09-01 08:35:11.976949+00	\N	\N	f
93	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxNzUyNC42OTE0MTgsImV4cCI6MTc1NzMyMjMyNC42OTE0MTgsIm5iZiI6MTc1NjcxNzUyNC42OTE0MTh9.__xpSlW4m_VCEYf9qMqG40G71zBbQM2g-IupoO3JFps	2025-09-08 09:05:24.691464+00	2025-09-01 09:05:24.685397+00	\N	\N	f
94	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxNzU2OS45NTYyNTQsImV4cCI6MTc1NzMyMjM2OS45NTYyNTQsIm5iZiI6MTc1NjcxNzU2OS45NTYyNTR9.IcVPzKo4jVWQPmO5oyWYDETDN-L2b7hIGoTcodWlFHc	2025-09-08 09:06:09.956301+00	2025-09-01 09:06:09.952732+00	\N	\N	f
95	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxNzYxNC40ODY2MDgsImV4cCI6MTc1NzMyMjQxNC40ODY2MDgsIm5iZiI6MTc1NjcxNzYxNC40ODY2MDh9.atY4c6MdcKRoIDDTad2BTfqUiQq3vo7Z3SEtxDGutyY	2025-09-08 09:06:54.486667+00	2025-09-01 09:06:54.482866+00	\N	\N	f
96	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxODMzNS44Mzc2MDksImV4cCI6MTc1NzMyMzEzNS44Mzc2MDksIm5iZiI6MTc1NjcxODMzNS44Mzc2MDl9.NJntzdGUS3navYoCq9owjtZ25min4_Hgw9xqmOwH1Ps	2025-09-08 09:18:55.837657+00	2025-09-01 09:18:55.831494+00	\N	\N	f
97	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxODkzOC44ODM5MzIsImV4cCI6MTc1NzMyMzczOC44ODM5MzIsIm5iZiI6MTc1NjcxODkzOC44ODM5MzJ9.BL-waUdcghjrwVObdIWUHl_TydM1gBxnMRCZdxB4P3k	2025-09-08 09:28:58.883979+00	2025-09-01 09:28:58.878221+00	\N	\N	f
98	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcxOTk4MC4zNzgxMTQsImV4cCI6MTc1NzMyNDc4MC4zNzgxMTQsIm5iZiI6MTc1NjcxOTk4MC4zNzgxMTR9.-ggf2BBPRMBItLz523sQzfx0jKD0tVffrMcuD83eI1E	2025-09-08 09:46:20.378163+00	2025-09-01 09:46:20.372664+00	\N	\N	f
99	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjcyMDg5OS43MTY4MzcsImV4cCI6MTc1NzMyNTY5OS43MTY4MzcsIm5iZiI6MTc1NjcyMDg5OS43MTY4Mzd9.JVMsDP-jwxOkAPtFx5zSpknKP14g_K8eAjXRHLl_R4M	2025-09-08 10:01:39.716882+00	2025-09-01 10:01:39.708858+00	\N	\N	f
100	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjczMDMxNi4xNDMwMjYsImV4cCI6MTc1NzMzNTExNi4xNDMwMjYsIm5iZiI6MTc1NjczMDMxNi4xNDMwMjZ9.YEo_GucfZXwuG2X12zRDWkqnfuutQ3UyZwTA-sbm4Ag	2025-09-08 12:38:36.143094+00	2025-09-01 12:38:36.134314+00	\N	\N	f
101	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjczMTI1NC44ODUyNTgsImV4cCI6MTc1NzMzNjA1NC44ODUyNTgsIm5iZiI6MTc1NjczMTI1NC44ODUyNTh9.lfGOSyk9ST-A0o-8aPA-N7RwtQZexFXDS7pJYOKyH30	2025-09-08 12:54:14.885305+00	2025-09-01 12:54:14.878231+00	\N	\N	f
102	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjczNDU3MS4wNzYzNDIsImV4cCI6MTc1NzMzOTM3MS4wNzYzNDIsIm5iZiI6MTc1NjczNDU3MS4wNzYzNDJ9.XmHuvjvWDN1Iby8BlPAQ2kuAz1uqYNjOf9VnmxDZ0gM	2025-09-08 13:49:31.07639+00	2025-09-01 13:49:31.070945+00	\N	\N	f
103	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc2Nzc4MS42ODY2NDUsImV4cCI6MTc1NzM3MjU4MS42ODY2NDUsIm5iZiI6MTc1Njc2Nzc4MS42ODY2NDV9.SP2ogP87qaTpZGVTH9VSYxW3l5cxokw4G9l2ryN3Xns	2025-09-08 23:03:01.686723+00	2025-09-01 23:03:01.681266+00	\N	\N	f
104	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc3NDc5MC4yNDI4MTgsImV4cCI6MTc1NzM3OTU5MC4yNDI4MTgsIm5iZiI6MTc1Njc3NDc5MC4yNDI4MTh9.jezeqlghjlb0KnbE-QWbpIYsY2r3gXvlXugUvzR6zKg	2025-09-09 00:59:50.242862+00	2025-09-02 00:59:50.237163+00	\N	\N	f
105	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc3NzE3MS4zNDg0NTYsImV4cCI6MTc1NzM4MTk3MS4zNDg0NTYsIm5iZiI6MTc1Njc3NzE3MS4zNDg0NTZ9.qInJu5eCZiH6p4UNDtDkUCjthHKL8OcYK3-Tu8wc1nI	2025-09-09 01:39:31.348503+00	2025-09-02 01:39:31.343373+00	\N	\N	f
106	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc3ODE3My41NTM1MTEsImV4cCI6MTc1NzM4Mjk3My41NTM1MTEsIm5iZiI6MTc1Njc3ODE3My41NTM1MTF9.EH3V-PSbLR0t3SGlEIU6IV9YtEtJ3w3WWxfSjLJBGRc	2025-09-09 01:56:13.553559+00	2025-09-02 01:56:13.54812+00	\N	\N	f
107	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc4MDUwMy4yOTEzMzUsImV4cCI6MTc1NzM4NTMwMy4yOTEzMzUsIm5iZiI6MTc1Njc4MDUwMy4yOTEzMzV9.7S7Rti-Au8VHiZXN8VWrda19UqbhenlA2FaJxE6nPtY	2025-09-09 02:35:03.29138+00	2025-09-02 02:35:03.285611+00	\N	\N	f
108	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc4MjA2Ny4xNjAwODMsImV4cCI6MTc1NzM4Njg2Ny4xNjAwODMsIm5iZiI6MTc1Njc4MjA2Ny4xNjAwODN9.YBiykYcxwbbv7VCSjXf2cUD8ryJSGSBnd-expPvXlYc	2025-09-09 03:01:07.160151+00	2025-09-02 03:01:07.15498+00	\N	\N	f
109	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc4MzQwOS41NTI4NDksImV4cCI6MTc1NzM4ODIwOS41NTI4NDksIm5iZiI6MTc1Njc4MzQwOS41NTI4NDl9.iAGqaD4Xitee_SJEY2He0IlQ4tN4sFqdrkK8PB_X35c	2025-09-09 03:23:29.552898+00	2025-09-02 03:23:29.547722+00	\N	\N	f
110	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc5MDYwNS40MjE0NSwiZXhwIjoxNzU3Mzk1NDA1LjQyMTQ1LCJuYmYiOjE3NTY3OTA2MDUuNDIxNDV9.Tzwm35t_yM4F8ko6TX2YQ1jSjjj8fS1vic8EItMNmkA	2025-09-09 05:23:25.421547+00	2025-09-02 05:23:25.414719+00	\N	\N	f
111	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc5MjQxMC44MTUwOTMsImV4cCI6MTc1NzM5NzIxMC44MTUwOTMsIm5iZiI6MTc1Njc5MjQxMC44MTUwOTN9.56iGeT8iBrE41DtuCprcsEBxiQcZdmdNF6ZGZsLxKYY	2025-09-09 05:53:30.81514+00	2025-09-02 05:53:30.809284+00	\N	\N	f
112	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc5MzkwOS4yNTI2MzUsImV4cCI6MTc1NzM5ODcwOS4yNTI2MzUsIm5iZiI6MTc1Njc5MzkwOS4yNTI2MzV9.fhX9fSBoSoQM6MCLFTiqFt0LQfP8MBpPNe6uapQp3tA	2025-09-09 06:18:29.252684+00	2025-09-02 06:18:29.246346+00	\N	\N	f
113	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc5NTQyNC45NjEyMjQsImV4cCI6MTc1NzQwMDIyNC45NjEyMjQsIm5iZiI6MTc1Njc5NTQyNC45NjEyMjR9.ZaRPp5pxevKb-CoXiN7mgfNGBMk_0Or5IMonTokT9cc	2025-09-09 06:43:44.961274+00	2025-09-02 06:43:44.944984+00	\N	\N	f
114	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc5Njg4MS4yMjIxMDEsImV4cCI6MTc1NzQwMTY4MS4yMjIxMDEsIm5iZiI6MTc1Njc5Njg4MS4yMjIxMDF9.9qdmrH2vyIxCt6GdxgIAMaTOhU_KtJZm5D8F-I1jxK8	2025-09-09 07:08:01.222153+00	2025-09-02 07:08:01.207029+00	\N	\N	f
115	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc5NzgxOS45MzIzMiwiZXhwIjoxNzU3NDAyNjE5LjkzMjMyLCJuYmYiOjE3NTY3OTc4MTkuOTMyMzJ9.AG2WXRI55-rkXJiSpqR3Yx97LEJBep7rCGKKlfrl62k	2025-09-09 07:23:39.932366+00	2025-09-02 07:23:39.926366+00	\N	\N	f
116	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njc5OTA0MC42MDE2OTcsImV4cCI6MTc1NzQwMzg0MC42MDE2OTcsIm5iZiI6MTc1Njc5OTA0MC42MDE2OTd9.qg_Y7Ox7KCf-EQa7tCQNBIMiIAW9R9LHW3SnYKfF9kU	2025-09-09 07:44:00.601748+00	2025-09-02 07:44:00.594787+00	\N	\N	f
117	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjgwMDA1MS4xOTIxNTIsImV4cCI6MTc1NzQwNDg1MS4xOTIxNTIsIm5iZiI6MTc1NjgwMDA1MS4xOTIxNTJ9.gy6syzFIlDuUZ2anNVyh97bUWcTAC_5D_tbvaHIdIsA	2025-09-09 08:00:51.1922+00	2025-09-02 08:00:51.181116+00	\N	\N	f
118	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjgwNDc4Mi41MjAxODksImV4cCI6MTc1NzQwOTU4Mi41MjAxODksIm5iZiI6MTc1NjgwNDc4Mi41MjAxODl9.E2C4x_VRxvTkM9vrNZOiY8-xtTNBwHiNnx0IpIqqeZI	2025-09-09 09:19:42.520281+00	2025-09-02 09:19:42.513705+00	\N	\N	f
119	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjgwNTEyNC4xMjkzODIsImV4cCI6MTc1NzQwOTkyNC4xMjkzODIsIm5iZiI6MTc1NjgwNTEyNC4xMjkzODJ9.u2LhmSdiMs8mbXW61F5RU1_sGfnJN3rE6Mq3hohcKQU	2025-09-09 09:25:24.12952+00	2025-09-02 09:25:24.12076+00	\N	\N	f
120	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjgwNTE0NS4zNDU2NzYsImV4cCI6MTc1NzQwOTk0NS4zNDU2NzYsIm5iZiI6MTc1NjgwNTE0NS4zNDU2NzZ9.ikfG213b5-gDnZiAUgf4viZYtJ1AGUyCcEukgskbWZc	2025-09-09 09:25:45.345723+00	2025-09-02 09:25:45.342713+00	\N	\N	f
121	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjgwNjYxOC43Mjk1MDQsImV4cCI6MTc1NzQxMTQxOC43Mjk1MDQsIm5iZiI6MTc1NjgwNjYxOC43Mjk1MDR9.lVqUYUwIwz6m3BGDw9S87Ujs8ild4PhLQMf2QUMr3uk	2025-09-09 09:50:18.729549+00	2025-09-02 09:50:18.72418+00	\N	\N	f
122	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjgyMDUwNi40NzAyMjcsImV4cCI6MTc1NzQyNTMwNi40NzAyMjcsIm5iZiI6MTc1NjgyMDUwNi40NzAyMjd9.cQf7FEnwrA_yUmU3rkF3Yiy5AHFq0lw71OSFejNUyoU	2025-09-09 13:41:46.470293+00	2025-09-02 13:41:46.456931+00	\N	\N	f
123	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NjgyMzAzMy4xMzkyNjYsImV4cCI6MTc1NzQyNzgzMy4xMzkyNjYsIm5iZiI6MTc1NjgyMzAzMy4xMzkyNjZ9.yTKj52kg1XY7zbQBywych0yPuNdCuOnswtw2JThUoIM	2025-09-09 14:23:53.139316+00	2025-09-02 14:23:53.134077+00	\N	\N	f
124	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg0OTAzNC40OTc1MTUsImV4cCI6MTc1NzQ1MzgzNC40OTc1MTUsIm5iZiI6MTc1Njg0OTAzNC40OTc1MTV9.NRTdoszWNomAKXeUqUTmv_rB-60_5Wk281HS1sInZZo	2025-09-09 21:37:14.497559+00	2025-09-02 21:37:14.491647+00	\N	\N	f
125	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg1Mjk4Mi42MTAwMzgsImV4cCI6MTc1NzQ1Nzc4Mi42MTAwMzgsIm5iZiI6MTc1Njg1Mjk4Mi42MTAwMzh9.TMNH6iUZx7AU_y0JJcO7LX5RfYnlszIXMdRmbfW0TUE	2025-09-09 22:43:02.610082+00	2025-09-02 22:43:02.600461+00	\N	\N	f
126	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg1Mzk1OC4wNTYzMjYsImV4cCI6MTc1NzQ1ODc1OC4wNTYzMjYsIm5iZiI6MTc1Njg1Mzk1OC4wNTYzMjZ9.QR8pee5B3Fd4koX3cHH7mxeESsamd_ZZ2xXwI0rRcHQ	2025-09-09 22:59:18.056374+00	2025-09-02 22:59:18.051174+00	\N	\N	f
127	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg2MzM1My4zMjQxMDUsImV4cCI6MTc1NzQ2ODE1My4zMjQxMDUsIm5iZiI6MTc1Njg2MzM1My4zMjQxMDV9.FZS9syOLk5_Ndt18qfwRV9-rI1gCAr3FKV-n6usHtDk	2025-09-10 01:35:53.32415+00	2025-09-03 01:35:53.317491+00	\N	\N	f
128	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg3MTU3OS44MTQxNzIsImV4cCI6MTc1NzQ3NjM3OS44MTQxNzIsIm5iZiI6MTc1Njg3MTU3OS44MTQxNzJ9.72RxxgDcX8LJCJkvE6kFj9otHDY6whBTdxY2nQKZO2o	2025-09-10 03:52:59.814273+00	2025-09-03 03:52:59.806954+00	\N	\N	f
129	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg3Mjc5Mi45NzQwMDgsImV4cCI6MTc1NzQ3NzU5Mi45NzQwMDgsIm5iZiI6MTc1Njg3Mjc5Mi45NzQwMDh9.CRqPvbEHFpRpgvyaJCHECQNba_m1NGpFXODeQvnd2V0	2025-09-10 04:13:12.974054+00	2025-09-03 04:13:12.96892+00	\N	\N	f
130	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg3Mzk4NS43OTc1NzYsImV4cCI6MTc1NzQ3ODc4NS43OTc1NzYsIm5iZiI6MTc1Njg3Mzk4NS43OTc1NzZ9.zawjc6KKEtjP6rJxrdT3TEoJI95O2TnJCs1fAT83QrY	2025-09-10 04:33:05.797623+00	2025-09-03 04:33:05.790386+00	\N	\N	f
131	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg3NTgzNi44ODY4ODEsImV4cCI6MTc1NzQ4MDYzNi44ODY4ODEsIm5iZiI6MTc1Njg3NTgzNi44ODY4ODF9.bAk9CNS3_ieTMgVXL9YuScQ06AHozPkkdy8l-r4RRzo	2025-09-10 05:03:56.886931+00	2025-09-03 05:03:56.871729+00	\N	\N	f
132	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg3OTQzNS44Mzc1NTcsImV4cCI6MTc1NzQ4NDIzNS44Mzc1NTcsIm5iZiI6MTc1Njg3OTQzNS44Mzc1NTd9.uHOZiLSJrkVY0gVweoKo3MeeD6K4YSCIgqs6qPqqU_Q	2025-09-10 06:03:55.837607+00	2025-09-03 06:03:55.831082+00	\N	\N	f
133	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg4Njk1Ny42NzM5OTIsImV4cCI6MTc1NzQ5MTc1Ny42NzM5OTIsIm5iZiI6MTc1Njg4Njk1Ny42NzM5OTJ9.dN3eb7KYLTXaRq2bGmOjD7sPSf4Yug7S8mgJ_Rz3Qv8	2025-09-10 08:09:17.674046+00	2025-09-03 08:09:17.654851+00	\N	\N	f
134	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njg5MjM1Ni42MTE1ODcsImV4cCI6MTc1NzQ5NzE1Ni42MTE1ODcsIm5iZiI6MTc1Njg5MjM1Ni42MTE1ODd9.cwVPSbZ9KQgPCb9PADLaPvAXGzO5jA2RBknvxI15HJQ	2025-09-10 09:39:16.611636+00	2025-09-03 09:39:16.606127+00	\N	\N	f
135	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njk1ODY2My4xOTA3NiwiZXhwIjoxNzU3NTYzNDYzLjE5MDc2LCJuYmYiOjE3NTY5NTg2NjMuMTkwNzZ9.QF9W62fj49Q1Rp-NBV6EZu8nQXHSyoaKjxxHcjZjbWs	2025-09-11 04:04:23.190808+00	2025-09-04 04:04:23.185167+00	\N	\N	f
136	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njk3MjQyNC45MTI4MzcsImV4cCI6MTc1NzU3NzIyNC45MTI4MzcsIm5iZiI6MTc1Njk3MjQyNC45MTI4Mzd9.T1W8azjYJxqL_CM15aVBGo80QT4pHDl-TKwlMTu-mcY	2025-09-11 07:53:44.91289+00	2025-09-04 07:53:44.907119+00	\N	\N	f
137	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njk3MzQzNS45MzQwODUsImV4cCI6MTc1NzU3ODIzNS45MzQwODUsIm5iZiI6MTc1Njk3MzQzNS45MzQwODV9.gaTt0tuCXtdeiQVR893z6OAx-6MiOBlYxoQT9S-82rQ	2025-09-11 08:10:35.934132+00	2025-09-04 08:10:35.928562+00	\N	\N	f
138	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njk3MzU5Ny43NjM0ODgsImV4cCI6MTc1NzU3ODM5Ny43NjM0ODgsIm5iZiI6MTc1Njk3MzU5Ny43NjM0ODh9.T-XluML51kiOLf8XpIy6weu_nOTvCZ70lZGm-mBG9rU	2025-09-11 08:13:17.763537+00	2025-09-04 08:13:17.759922+00	\N	\N	f
139	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njk3NDkyNi41MzQ3MywiZXhwIjoxNzU3NTc5NzI2LjUzNDczLCJuYmYiOjE3NTY5NzQ5MjYuNTM0NzN9.GM2xgWhfJ7D2-NpQwH3W2AqbVgJXrgjdyORpBg1a5pg	2025-09-11 08:35:26.534776+00	2025-09-04 08:35:26.529552+00	\N	\N	f
140	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Njk3OTQ4OC44NDk2NzQsImV4cCI6MTc1NzU4NDI4OC44NDk2NzQsIm5iZiI6MTc1Njk3OTQ4OC44NDk2NzR9.92d2iOFsLCgJMVr-RsHDdf1v3fEtq13StcTPcCa4OZI	2025-09-11 09:51:28.849723+00	2025-09-04 09:51:28.844109+00	\N	\N	f
141	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzAyMTg5NC4yMTM5MTIsImV4cCI6MTc1NzYyNjY5NC4yMTM5MTIsIm5iZiI6MTc1NzAyMTg5NC4yMTM5MTJ9.8pHtN000Fsi2F_Nzac44Cj4StEaFIh-6HN3q-pQTyZQ	2025-09-11 21:38:14.213995+00	2025-09-04 21:38:14.208753+00	\N	\N	f
142	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzAyNzU5Mi45OTE1ODIsImV4cCI6MTc1NzYzMjM5Mi45OTE1ODIsIm5iZiI6MTc1NzAyNzU5Mi45OTE1ODJ9.oXBbQBlloxA-z5dluikh3XS2xod008jzs2AYs3h5cqM	2025-09-11 23:13:12.991631+00	2025-09-04 23:13:12.976217+00	\N	\N	f
143	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzAzMTM1OS4zOTE1MjcsImV4cCI6MTc1NzYzNjE1OS4zOTE1MjcsIm5iZiI6MTc1NzAzMTM1OS4zOTE1Mjd9.uJuxnoeCN5vyOSYea7bSHkHbGW4cOX0vDmrYVX-igqY	2025-09-12 00:15:59.391593+00	2025-09-05 00:15:59.385432+00	\N	\N	f
144	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzI1MDA5NS43NDI3NjcsImV4cCI6MTc1Nzg1NDg5NS43NDI3NjcsIm5iZiI6MTc1NzI1MDA5NS43NDI3Njd9.C3dtCtP_IZgBsi6Ekdrg34A23TIGHetavPvEJNMINkw	2025-09-14 13:01:35.742821+00	2025-09-07 13:01:35.737629+00	\N	\N	f
145	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzI1MDExNC43NTA5MDMsImV4cCI6MTc1Nzg1NDkxNC43NTA5MDMsIm5iZiI6MTc1NzI1MDExNC43NTA5MDN9.Xl17z9GmxX7GdEKrrPPQAQNj4HbVzsXLfmuLAj0Vs2E	2025-09-14 13:01:54.750948+00	2025-09-07 13:01:54.747031+00	\N	\N	f
146	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzI4NTk3My42OTg1OTcsImV4cCI6MTc1Nzg5MDc3My42OTg1OTcsIm5iZiI6MTc1NzI4NTk3My42OTg1OTd9.ad3Yp8o6Kr6EKPGL7vbMv4QPKcMyRP4QCIcW6xwKhN4	2025-09-14 22:59:33.698656+00	2025-09-07 22:59:33.690754+00	\N	\N	f
147	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzQ4MDcyNy4wOTE5NzcsImV4cCI6MTc1ODA4NTUyNy4wOTE5NzcsIm5iZiI6MTc1NzQ4MDcyNy4wOTE5Nzd9.5UuNGnhXXUusCubNAcWeT_d2s89dsrBio9SsGqmJf6A	2025-09-17 05:05:27.092026+00	2025-09-10 05:05:27.086713+00	\N	\N	f
148	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzQ4MzU3MS44NDQ2ODYsImV4cCI6MTc1ODA4ODM3MS44NDQ2ODYsIm5iZiI6MTc1NzQ4MzU3MS44NDQ2ODZ9.n5y4mN4SBK30SXxk-OFwVD3e-jcZRN7hcCaAlWxZutg	2025-09-17 05:52:51.844745+00	2025-09-10 05:52:51.837895+00	\N	\N	f
149	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzQ4ODk4My43MTAxNzgsImV4cCI6MTc1ODA5Mzc4My43MTAxNzgsIm5iZiI6MTc1NzQ4ODk4My43MTAxNzh9.4UcSf-ocFfpifiT_KEbeNPSLkrheYEcja1AO3BUyxgA	2025-09-17 07:23:03.710225+00	2025-09-10 07:23:03.703638+00	\N	\N	f
150	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzQ5MzY4Ni41MTYyOTMsImV4cCI6MTc1ODA5ODQ4Ni41MTYyOTMsIm5iZiI6MTc1NzQ5MzY4Ni41MTYyOTN9.wsmnk1fSmTnBjrqSzaqNcz6rrim_bJzCeGbHnz-sIgw	2025-09-17 08:41:26.516339+00	2025-09-10 08:41:26.510334+00	\N	\N	f
151	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzQ5NDY0OC4yNzE1NDMsImV4cCI6MTc1ODA5OTQ0OC4yNzE1NDMsIm5iZiI6MTc1NzQ5NDY0OC4yNzE1NDN9.mtq2xlX61Uy9jOud9IelFI15aIjoGQ54E-2z4z9UYcM	2025-09-17 08:57:28.271591+00	2025-09-10 08:57:28.266634+00	\N	\N	f
152	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzQ5OTI4OS45OTU4NjIsImV4cCI6MTc1ODEwNDA4OS45OTU4NjIsIm5iZiI6MTc1NzQ5OTI4OS45OTU4NjJ9.seC1ORB3FpgolG3f6VTfrtLHkny2yT2EWrVOauSXa0o	2025-09-17 10:14:49.99591+00	2025-09-10 10:14:49.990637+00	\N	\N	f
153	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU0MDM4MS41ODM5MjYsImV4cCI6MTc1ODE0NTE4MS41ODM5MjYsIm5iZiI6MTc1NzU0MDM4MS41ODM5MjZ9.L0EAYNbsaUFNKNoXmUsK-v1LKGlVN3yL8z9Sxa9NuV8	2025-09-17 21:39:41.583992+00	2025-09-10 21:39:41.576708+00	\N	\N	f
154	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU0MjM4NS4wMjEyMTcsImV4cCI6MTc1ODE0NzE4NS4wMjEyMTcsIm5iZiI6MTc1NzU0MjM4NS4wMjEyMTd9.ptleGlXHjymFTfgqC4e0H1icnoPTI8rrn2h1nzqv87A	2025-09-17 22:13:05.021261+00	2025-09-10 22:13:05.016063+00	\N	\N	f
155	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU0MzQxMy4zNTI3MzUsImV4cCI6MTc1ODE0ODIxMy4zNTI3MzUsIm5iZiI6MTc1NzU0MzQxMy4zNTI3MzV9.el9BjIZsN7jWPQiQ4QGfMg7P1eNTzDIhtl8vXFxKDXY	2025-09-17 22:30:13.352782+00	2025-09-10 22:30:13.347439+00	\N	\N	f
156	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU0NDMxNS4yMjE5NTksImV4cCI6MTc1ODE0OTExNS4yMjE5NTksIm5iZiI6MTc1NzU0NDMxNS4yMjE5NTl9.vEDMTt-d1r1CSaL1y9QZMfeFsOcfayLiOhRXJw-IpBk	2025-09-17 22:45:15.222005+00	2025-09-10 22:45:15.215954+00	\N	\N	f
157	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU1NzA4MC4zMjg3NjYsImV4cCI6MTc1ODE2MTg4MC4zMjg3NjYsIm5iZiI6MTc1NzU1NzA4MC4zMjg3NjZ9.VjlJEK_8Fgr5sKoQU4FY0kGD_dS7uunsbm0O269ELqA	2025-09-18 02:18:00.328811+00	2025-09-11 02:18:00.322873+00	\N	\N	f
158	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU2MjQxMS45MzEyNzEsImV4cCI6MTc1ODE2NzIxMS45MzEyNzEsIm5iZiI6MTc1NzU2MjQxMS45MzEyNzF9.Rq4hg0TKgLOE2imx0ej46hzD4RsSTuivFmp2guBAZwE	2025-09-18 03:46:51.931319+00	2025-09-11 03:46:51.925739+00	\N	\N	f
159	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU2NDQwNC4wMjc4MjQsImV4cCI6MTc1ODE2OTIwNC4wMjc4MjQsIm5iZiI6MTc1NzU2NDQwNC4wMjc4MjR9.i3zPiak4LvqW7efywVDxl6Witj0UPBPqUMxIKiRSX00	2025-09-18 04:20:04.027875+00	2025-09-11 04:20:04.013823+00	\N	\N	f
160	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU2NTUwNC4yNDAxNCwiZXhwIjoxNzU4MTcwMzA0LjI0MDE0LCJuYmYiOjE3NTc1NjU1MDQuMjQwMTR9.4yAo0l87jjELtTmvYUOVSA2uRjkoOpiJDMHclcmf3ZI	2025-09-18 04:38:24.240214+00	2025-09-11 04:38:24.231112+00	\N	\N	f
161	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU3MzYxNS41MDk0MjYsImV4cCI6MTc1ODE3ODQxNS41MDk0MjYsIm5iZiI6MTc1NzU3MzYxNS41MDk0MjZ9.I5WIhOvqOks3XYaimE4KXyeAyHvZwbV3CSvuuiuqPEw	2025-09-18 06:53:35.509475+00	2025-09-11 06:53:35.503449+00	\N	\N	f
162	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU3NDU4Ny4yMDYxMzcsImV4cCI6MTc1ODE3OTM4Ny4yMDYxMzcsIm5iZiI6MTc1NzU3NDU4Ny4yMDYxMzd9.my9dVUgDyqATZidT9rPyY4deg9vILm75yKf1VHPX5AE	2025-09-18 07:09:47.206215+00	2025-09-11 07:09:47.199115+00	\N	\N	f
163	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU3NTUwOS44MTU1NDMsImV4cCI6MTc1ODE4MDMwOS44MTU1NDMsIm5iZiI6MTc1NzU3NTUwOS44MTU1NDN9.KVYHmehshGGtr6fIIb2t5h-d94DDqT7bJJIpEJWevc4	2025-09-18 07:25:09.815661+00	2025-09-11 07:25:09.808091+00	\N	\N	f
164	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU3NzU3OC40MDU3NDEsImV4cCI6MTc1ODE4MjM3OC40MDU3NDEsIm5iZiI6MTc1NzU3NzU3OC40MDU3NDF9.gKHes_3ZtblRGNrvgk9RuX22ifBsutx5nEBpUNVEtak	2025-09-18 07:59:38.405789+00	2025-09-11 07:59:38.399944+00	\N	\N	f
165	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU4NjU3OC45ODE5NzksImV4cCI6MTc1ODE5MTM3OC45ODE5NzksIm5iZiI6MTc1NzU4NjU3OC45ODE5Nzl9.NQzlN3q7VFLVUl4MNzGyNjD1bqliXcI1nj_u1l3SMWk	2025-09-18 10:29:38.982024+00	2025-09-11 10:29:38.974941+00	\N	\N	f
166	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzU4Nzk2OS41NDY4NzgsImV4cCI6MTc1ODE5Mjc2OS41NDY4NzgsIm5iZiI6MTc1NzU4Nzk2OS41NDY4Nzh9.0pnj79BybtrXWOxHA8XA7Sj1WKbmaMcYBWMQ_VWNDV0	2025-09-18 10:52:49.546922+00	2025-09-11 10:52:49.541734+00	\N	\N	f
167	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzYzNjA5MS4yMTU0NTcsImV4cCI6MTc1ODI0MDg5MS4yMTU0NTcsIm5iZiI6MTc1NzYzNjA5MS4yMTU0NTd9.WKs6TacznyFctEeiXY2ooVLwPUNaN-hKuenYOScVC9w	2025-09-19 00:14:51.215502+00	2025-09-12 00:14:51.209497+00	\N	\N	f
168	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzYzNzcyMC42MDY5NTEsImV4cCI6MTc1ODI0MjUyMC42MDY5NTEsIm5iZiI6MTc1NzYzNzcyMC42MDY5NTF9.ZrF5Xo-0WL7NvK-AjVeTFwQ6EinjM7JmKcqi2OSXVJw	2025-09-19 00:42:00.607007+00	2025-09-12 00:42:00.60121+00	\N	\N	f
169	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzY0MzAyOC43NTAwMjcsImV4cCI6MTc1ODI0NzgyOC43NTAwMjcsIm5iZiI6MTc1NzY0MzAyOC43NTAwMjd9.u_Mjc472qLELzQqznIBukCmC1iAL1ttHmkuiBmz74e4	2025-09-19 02:10:28.750077+00	2025-09-12 02:10:28.735553+00	\N	\N	f
170	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzcxNTIzOC4yNzcyOTUsImV4cCI6MTc1ODMyMDAzOC4yNzcyOTUsIm5iZiI6MTc1NzcxNTIzOC4yNzcyOTV9.LAtGWWxdLq16BGN2oPJCdXjbcyWwG7eonh1ZW1V7M-U	2025-09-19 22:13:58.277344+00	2025-09-12 22:13:58.271919+00	\N	\N	f
171	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzcxNjE4OC40ODk4NDIsImV4cCI6MTc1ODMyMDk4OC40ODk4NDIsIm5iZiI6MTc1NzcxNjE4OC40ODk4NDJ9.yE2YmODN7JFt2p1kK-caQzriveS3jtNJPkuYQG53GXE	2025-09-19 22:29:48.489887+00	2025-09-12 22:29:48.484121+00	\N	\N	f
172	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzcxNzIyMi4zNDQ5MjEsImV4cCI6MTc1ODMyMjAyMi4zNDQ5MjEsIm5iZiI6MTc1NzcxNzIyMi4zNDQ5MjF9.N7kKqGXXLAiKrxxokzDevrrh4kCPjToJi9O9chKhrSs	2025-09-19 22:47:02.344968+00	2025-09-12 22:47:02.339421+00	\N	\N	f
173	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzcxODU0MS45Njk3MDIsImV4cCI6MTc1ODMyMzM0MS45Njk3MDIsIm5iZiI6MTc1NzcxODU0MS45Njk3MDJ9.6D17srf-N9AetjhnhM1Mnykj63CflYy8VnWmeCWK6Kg	2025-09-19 23:09:01.969749+00	2025-09-12 23:09:01.948592+00	\N	\N	f
174	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzcxOTQ0My42MDA3MDksImV4cCI6MTc1ODMyNDI0My42MDA3MDksIm5iZiI6MTc1NzcxOTQ0My42MDA3MDl9.wcrdOLvEKbhPQyfMXScuFoAkOtif3NlgksuFKvMqpMo	2025-09-19 23:24:03.600803+00	2025-09-12 23:24:03.592265+00	\N	\N	f
175	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzczMTAyNC4zOTMxNzgsImV4cCI6MTc1ODMzNTgyNC4zOTMxNzgsIm5iZiI6MTc1NzczMTAyNC4zOTMxNzh9.LaaB3bgu46c11NhnckcJigvzXgirqXNpAh-KJ3v1JK0	2025-09-20 02:37:04.39323+00	2025-09-13 02:37:04.387274+00	\N	\N	f
176	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzczMTk0Mi45OTg5OTEsImV4cCI6MTc1ODMzNjc0Mi45OTg5OTEsIm5iZiI6MTc1NzczMTk0Mi45OTg5OTF9.schYEIwns9QbefDq_vRzYTgj10o0NXHMt-OyOW4x4tw	2025-09-20 02:52:22.999038+00	2025-09-13 02:52:22.982853+00	\N	\N	f
177	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzczMjg2MC41OTEzMzgsImV4cCI6MTc1ODMzNzY2MC41OTEzMzgsIm5iZiI6MTc1NzczMjg2MC41OTEzMzh9._FzsyHdZcB3u_uHoJkixAmNW-C-Tj7H4BtBkvS902Xk	2025-09-20 03:07:40.591391+00	2025-09-13 03:07:40.585455+00	\N	\N	f
178	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzczNjc0NS4xNTk1MDksImV4cCI6MTc1ODM0MTU0NS4xNTk1MDksIm5iZiI6MTc1NzczNjc0NS4xNTk1MDl9.q-3UBm-CtHaRIG9YNIA0mAmOqnDEoF1_-PstV-zLYXc	2025-09-20 04:12:25.159555+00	2025-09-13 04:12:25.153581+00	\N	\N	f
179	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzczNzk3MC40MDM2MDIsImV4cCI6MTc1ODM0Mjc3MC40MDM2MDIsIm5iZiI6MTc1NzczNzk3MC40MDM2MDJ9.mjFBtKUk31-aFHFh83LPwpKdqucTDIFfP30mRduflBI	2025-09-20 04:32:50.403657+00	2025-09-13 04:32:50.39781+00	\N	\N	f
180	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzczODg3OS44OTM4NDcsImV4cCI6MTc1ODM0MzY3OS44OTM4NDcsIm5iZiI6MTc1NzczODg3OS44OTM4NDd9.mXbEQ6WSDHe1Ihosz0qskU07v_ibhflBfiBVySXjP6I	2025-09-20 04:47:59.893898+00	2025-09-13 04:47:59.887742+00	\N	\N	f
181	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzczOTk2MC44NTA5ODksImV4cCI6MTc1ODM0NDc2MC44NTA5ODksIm5iZiI6MTc1NzczOTk2MC44NTA5ODl9.T2opjfpinyYFWul4-344hoHvMO4-tjkgx01BY9m7u_Y	2025-09-20 05:06:00.851223+00	2025-09-13 05:06:00.820728+00	\N	\N	f
182	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzc1MzM0MS41NjQzMTgsImV4cCI6MTc1ODM1ODE0MS41NjQzMTgsIm5iZiI6MTc1Nzc1MzM0MS41NjQzMTh9.P-UYrBtwhP3MKO0tDxZM3kKcMlY_oK69XjEg1sOa8UY	2025-09-20 08:49:01.564364+00	2025-09-13 08:49:01.558488+00	\N	\N	f
183	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzc1NDMxNS43MDkyNDgsImV4cCI6MTc1ODM1OTExNS43MDkyNDgsIm5iZiI6MTc1Nzc1NDMxNS43MDkyNDh9.Yrst7p7tBq9RBEE6W0SjQkfL_sIQ0lLvhulP7REyulo	2025-09-20 09:05:15.709318+00	2025-09-13 09:05:15.690256+00	\N	\N	f
184	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzc1NTcxOC4xNjQyMDQsImV4cCI6MTc1ODM2MDUxOC4xNjQyMDQsIm5iZiI6MTc1Nzc1NTcxOC4xNjQyMDR9.lxNXhc4wtesC16Gb35K4qL88KpjthK9b61z16BfUD-8	2025-09-20 09:28:38.164258+00	2025-09-13 09:28:38.158731+00	\N	\N	f
185	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzc1Nzc3OC4wODE1ODksImV4cCI6MTc1ODM2MjU3OC4wODE1ODksIm5iZiI6MTc1Nzc1Nzc3OC4wODE1ODl9.koNsLh255whLq1nHn0uD0Z2yq4N5OFVHTjLC3vDv4fE	2025-09-20 10:02:58.081634+00	2025-09-13 10:02:58.072529+00	\N	\N	f
186	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzgwMTU3OC4wOTgxMSwiZXhwIjoxNzU4NDA2Mzc4LjA5ODExLCJuYmYiOjE3NTc4MDE1NzguMDk4MTF9.0Tc7wpIIXuvN7vGKJm_tPhAVwZomW_myPfyz87SPDFw	2025-09-20 22:12:58.098158+00	2025-09-13 22:12:58.093077+00	\N	\N	f
187	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzgwMjY1OS4yMTg4MjgsImV4cCI6MTc1ODQwNzQ1OS4yMTg4MjgsIm5iZiI6MTc1NzgwMjY1OS4yMTg4Mjh9.AyMgT4WnBEYi7INPO5b-nI6NDZkT2vJlLQ4tsWKVkZ0	2025-09-20 22:30:59.218875+00	2025-09-13 22:30:59.21294+00	\N	\N	f
188	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzgwNDAyMS4zMzkzNywiZXhwIjoxNzU4NDA4ODIxLjMzOTM3LCJuYmYiOjE3NTc4MDQwMjEuMzM5Mzd9.QAMV_HwxXNwUE-Ql23Dgf0KgGlK5_mGZ7XUS2fxHSJM	2025-09-20 22:53:41.339424+00	2025-09-13 22:53:41.333611+00	\N	\N	f
189	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzgwNDk4My43NzM1NjQsImV4cCI6MTc1ODQwOTc4My43NzM1NjQsIm5iZiI6MTc1NzgwNDk4My43NzM1NjR9.jg-ZJVCXecbPFvINdpgQ3YKLnR9k3aUtB3GumPfDtmM	2025-09-20 23:09:43.773613+00	2025-09-13 23:09:43.768004+00	\N	\N	f
190	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzgwNTk2NS45MTIxMywiZXhwIjoxNzU4NDEwNzY1LjkxMjEzLCJuYmYiOjE3NTc4MDU5NjUuOTEyMTN9.9u4tlmKO2j8jSGjRYYMmM5NvffsgcsnfzWC1H77rBqI	2025-09-20 23:26:05.912178+00	2025-09-13 23:26:05.905977+00	\N	\N	f
191	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzgwNjg2OS4wOTEzNTMsImV4cCI6MTc1ODQxMTY2OS4wOTEzNTMsIm5iZiI6MTc1NzgwNjg2OS4wOTEzNTN9.C-h4tjjLVmDjXZPsF8Yh3Cx_5POmGzzKT3IATQxcHMY	2025-09-20 23:41:09.091412+00	2025-09-13 23:41:09.085835+00	\N	\N	f
192	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg1MzE1Mi4wNzU3NzksImV4cCI6MTc1ODQ1Nzk1Mi4wNzU3NzksIm5iZiI6MTc1Nzg1MzE1Mi4wNzU3Nzl9.4Dggq9jpLpcsC1Wp_xGxWKtqBVIH1d8P_jUachW3NoI	2025-09-21 12:32:32.075823+00	2025-09-14 12:32:32.069351+00	\N	\N	f
193	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg1MzI0MC44ODIyNjYsImV4cCI6MTc1ODQ1ODA0MC44ODIyNjYsIm5iZiI6MTc1Nzg1MzI0MC44ODIyNjZ9.iGCNriTa6K05ovAXEiX25CmbYfOXm-vAGoLiMGtKRRQ	2025-09-21 12:34:00.882343+00	2025-09-14 12:34:00.878497+00	\N	\N	f
194	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg1MzM0My42NjYxOTIsImV4cCI6MTc1ODQ1ODE0My42NjYxOTIsIm5iZiI6MTc1Nzg1MzM0My42NjYxOTJ9._dkxm8hXqhIAacLenQo7YHJBynZU1qqAabOJYiuJVvg	2025-09-21 12:35:43.666242+00	2025-09-14 12:35:43.66298+00	\N	\N	f
195	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg1MzQ2Ny42ODkxMjQsImV4cCI6MTc1ODQ1ODI2Ny42ODkxMjQsIm5iZiI6MTc1Nzg1MzQ2Ny42ODkxMjR9.DHciD5znnE4oefNl-oSEsknO65QwwNf0ZNtFS7TwZzY	2025-09-21 12:37:47.68917+00	2025-09-14 12:37:47.682877+00	\N	\N	f
196	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg1NDQ0Ny44MDcxNTEsImV4cCI6MTc1ODQ1OTI0Ny44MDcxNTEsIm5iZiI6MTc1Nzg1NDQ0Ny44MDcxNTF9.4xAby3ZYjSWRxLvFb89bDQXnzPo1tLXWsZ3g6JsAF6k	2025-09-21 12:54:07.807199+00	2025-09-14 12:54:07.79277+00	\N	\N	f
197	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg1NTM4NS4yMzUwNzgsImV4cCI6MTc1ODQ2MDE4NS4yMzUwNzgsIm5iZiI6MTc1Nzg1NTM4NS4yMzUwNzh9.Wwbyfjd7-qeP2a-YBHKfG8EQvlN3J-qCu6WHNYYO4Tg	2025-09-21 13:09:45.23513+00	2025-09-14 13:09:45.229033+00	\N	\N	f
198	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg1NjI5NC43MjE1MTksImV4cCI6MTc1ODQ2MTA5NC43MjE1MTksIm5iZiI6MTc1Nzg1NjI5NC43MjE1MTl9.Wk7lbxj27RxOKwh0PiKuvY-n4PNAm4WS4DL9R5X6ODU	2025-09-21 13:24:54.721566+00	2025-09-14 13:24:54.714996+00	\N	\N	f
199	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg4NDg4Ny42ODk5MDMsImV4cCI6MTc1ODQ4OTY4Ny42ODk5MDMsIm5iZiI6MTc1Nzg4NDg4Ny42ODk5MDN9.HbW93-9UBLeaW-ktFNf1GnYvFfjKFlI426Ymg_krJYQ	2025-09-21 21:21:27.689951+00	2025-09-14 21:21:27.68413+00	\N	\N	f
200	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg4NTgyMS4xNjQ2MzYsImV4cCI6MTc1ODQ5MDYyMS4xNjQ2MzYsIm5iZiI6MTc1Nzg4NTgyMS4xNjQ2MzZ9.7LfudfMgzsOTx9PDiztOjxpIiKydLAtz484Xcs7gcxU	2025-09-21 21:37:01.164683+00	2025-09-14 21:37:01.157805+00	\N	\N	f
201	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg4ODI1OC44MjIxMjYsImV4cCI6MTc1ODQ5MzA1OC44MjIxMjYsIm5iZiI6MTc1Nzg4ODI1OC44MjIxMjZ9.Cjd1gslnVN8Hwf_Ke3xFx_sCRpIiK_SK6ZJde0yDKyg	2025-09-21 22:17:38.822172+00	2025-09-14 22:17:38.815582+00	\N	\N	f
202	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg4OTI0Ny4zNjI3OTQsImV4cCI6MTc1ODQ5NDA0Ny4zNjI3OTQsIm5iZiI6MTc1Nzg4OTI0Ny4zNjI3OTR9.dQw3Oh5U8cktmyfgmP7IShz461mptOCVmlUe1GvtWXs	2025-09-21 22:34:07.362861+00	2025-09-14 22:34:07.356885+00	\N	\N	f
203	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzg5MDM5Ni4yMDk5MDYsImV4cCI6MTc1ODQ5NTE5Ni4yMDk5MDYsIm5iZiI6MTc1Nzg5MDM5Ni4yMDk5MDZ9.bqflJ5S5JG0epUajRLKL8s1Vlu4YTk5bNK0HCifsZNk	2025-09-21 22:53:16.209952+00	2025-09-14 22:53:16.203458+00	\N	\N	f
204	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkwMzE0Ny40NzcxNTksImV4cCI6MTc1ODUwNzk0Ny40NzcxNTksIm5iZiI6MTc1NzkwMzE0Ny40NzcxNTl9.UHXJOvmNH8feMeLVBDFZ5_cktTt8vgJz6xxnWa2n5Pk	2025-09-22 02:25:47.477207+00	2025-09-15 02:25:47.469961+00	\N	\N	f
205	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkwNDA4NS41NDk1MzgsImV4cCI6MTc1ODUwODg4NS41NDk1MzgsIm5iZiI6MTc1NzkwNDA4NS41NDk1Mzh9.WEcW5eEAn58CCH3WEMy71G6jPEdhlUvMwh6ix7-RPUs	2025-09-22 02:41:25.549588+00	2025-09-15 02:41:25.543936+00	\N	\N	f
206	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkwNTc4MC4xNjkzMDQsImV4cCI6MTc1ODUxMDU4MC4xNjkzMDQsIm5iZiI6MTc1NzkwNTc4MC4xNjkzMDR9.AqLzc2Shq4TxMfHmufQYGvVawPxK4IqBvXsYv6nTo-8	2025-09-22 03:09:40.169352+00	2025-09-15 03:09:40.163317+00	\N	\N	f
207	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkxMDAxMC4yOTEwNTcsImV4cCI6MTc1ODUxNDgxMC4yOTEwNTcsIm5iZiI6MTc1NzkxMDAxMC4yOTEwNTd9.JOlCwhwbw9dmjg8lbTLyBDzrAqvAMsPWmmgvQT7NytM	2025-09-22 04:20:10.291144+00	2025-09-15 04:20:10.284762+00	\N	\N	f
208	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkxMTA5NC4xNjcyMzcsImV4cCI6MTc1ODUxNTg5NC4xNjcyMzcsIm5iZiI6MTc1NzkxMTA5NC4xNjcyMzd9.KJLlH8YBfqbWho9Ah2hB2-0jXPiss7LfAqW_QhhgV1o	2025-09-22 04:38:14.167284+00	2025-09-15 04:38:14.161391+00	\N	\N	f
209	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkyMjI2Ni4xMDM4NzcsImV4cCI6MTc1ODUyNzA2Ni4xMDM4NzcsIm5iZiI6MTc1NzkyMjI2Ni4xMDM4Nzd9.-B9w1LTAKUe7OPv28xmjzuyX8amnTnUfCY7YjTI4w5E	2025-09-22 07:44:26.103928+00	2025-09-15 07:44:26.088623+00	\N	\N	f
210	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkyMzQwMy42NjUxNDEsImV4cCI6MTc1ODUyODIwMy42NjUxNDEsIm5iZiI6MTc1NzkyMzQwMy42NjUxNDF9.fXMR7geF81yZf5igzVhm6G0_IqdOs7mCxZhfOGMBKKI	2025-09-22 08:03:23.665188+00	2025-09-15 08:03:23.659209+00	\N	\N	f
211	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkyNDM0OC43Mjc2MzgsImV4cCI6MTc1ODUyOTE0OC43Mjc2MzgsIm5iZiI6MTc1NzkyNDM0OC43Mjc2Mzh9.sM4k1aKe0lQo3F6WAWCUkM1xtXnS7ZKZJea9f5aGkQs	2025-09-22 08:19:08.727692+00	2025-09-15 08:19:08.721432+00	\N	\N	f
212	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkyNjA3NS44NTQ3NjYsImV4cCI6MTc1ODUzMDg3NS44NTQ3NjYsIm5iZiI6MTc1NzkyNjA3NS44NTQ3NjZ9.qJ7fVNL109EtVCDMoyn0WxR7tfUB48Wv4dHHFMECMuc	2025-09-22 08:47:55.854813+00	2025-09-15 08:47:55.847696+00	\N	\N	f
213	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkyNzA3Mi43MzM0OTYsImV4cCI6MTc1ODUzMTg3Mi43MzM0OTYsIm5iZiI6MTc1NzkyNzA3Mi43MzM0OTZ9.R51APpm3MN6lql3gim9I70aYCqEdEt-HMSX2tDwySOI	2025-09-22 09:04:32.733542+00	2025-09-15 09:04:32.726608+00	\N	\N	f
214	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkyODAyMy44MjI1NzIsImV4cCI6MTc1ODUzMjgyMy44MjI1NzIsIm5iZiI6MTc1NzkyODAyMy44MjI1NzJ9.2qYth3dBw7U3RKwu6i_VEpL_9HHHK7VdQQLqHRqdHCc	2025-09-22 09:20:23.822619+00	2025-09-15 09:20:23.815092+00	\N	\N	f
215	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkyOTE3Ny4xOTY4MDIsImV4cCI6MTc1ODUzMzk3Ny4xOTY4MDIsIm5iZiI6MTc1NzkyOTE3Ny4xOTY4MDJ9.VgmPs0r2xWfDCX8LIB_zHX8NIql4bgR1VkHivXUFZ1E	2025-09-22 09:39:37.196851+00	2025-09-15 09:39:37.190899+00	\N	\N	f
216	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkzMDU5NC44MzAxNzMsImV4cCI6MTc1ODUzNTM5NC44MzAxNzMsIm5iZiI6MTc1NzkzMDU5NC44MzAxNzN9.uI2b0k8tfO09J8vcaBSeHrl3iLzKFn0EloD0B-J-iQk	2025-09-22 10:03:14.830221+00	2025-09-15 10:03:14.824182+00	\N	\N	f
217	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1NzkzMTY2MC40NzI1MjcsImV4cCI6MTc1ODUzNjQ2MC40NzI1MjcsIm5iZiI6MTc1NzkzMTY2MC40NzI1Mjd9.xk9GgvQau0t0gXAta87wU271-ow-AZXwB1qO39sQKts	2025-09-22 10:21:00.472576+00	2025-09-15 10:21:00.466577+00	\N	\N	f
218	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk0MTI0Mi40MTgyMzQsImV4cCI6MTc1ODU0NjA0Mi40MTgyMzQsIm5iZiI6MTc1Nzk0MTI0Mi40MTgyMzR9.i756bGx8GvrjKuuMdK_rxNXuCq_-cBRb9T63rqmJNHs	2025-09-22 13:00:42.418286+00	2025-09-15 13:00:42.409374+00	\N	\N	f
219	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk3MTIzMC44NTc5NjcsImV4cCI6MTc1ODU3NjAzMC44NTc5NjcsIm5iZiI6MTc1Nzk3MTIzMC44NTc5Njd9.MvE51qMh4c6_38qbnVVO7aSd1Ns-oKVd4kLmovn3g0M	2025-09-22 21:20:30.858012+00	2025-09-15 21:20:30.851649+00	\N	\N	f
220	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk3MjIxMS44MDc5NCwiZXhwIjoxNzU4NTc3MDExLjgwNzk0LCJuYmYiOjE3NTc5NzIyMTEuODA3OTR9.691_DQC2lFgtOWVVBLiYLcIWZPG8wOtLO644QW-xH6Q	2025-09-22 21:36:51.807985+00	2025-09-15 21:36:51.801604+00	\N	\N	f
221	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk3MjU1OC4wODMwMjYsImV4cCI6MTc1ODU3NzM1OC4wODMwMjYsIm5iZiI6MTc1Nzk3MjU1OC4wODMwMjZ9.zJDtHczF8jDB_3P23cv51rQ5O-0kA5loqEPiTBoWlD8	2025-09-22 21:42:38.083074+00	2025-09-15 21:42:38.076409+00	\N	\N	f
222	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk3NDkwMC43MjM3MzEsImV4cCI6MTc1ODU3OTcwMC43MjM3MzEsIm5iZiI6MTc1Nzk3NDkwMC43MjM3MzF9.9M55OuBujaAGPVKgMqtq2SYzlPNv2vlBASSX8GgBkHM	2025-09-22 22:21:40.723827+00	2025-09-15 22:21:40.715781+00	\N	\N	f
223	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk3NjE1My4wOTg2NSwiZXhwIjoxNzU4NTgwOTUzLjA5ODY1LCJuYmYiOjE3NTc5NzYxNTMuMDk4NjV9.w5TBNxtObCN1Fl7AhtGGV-TCMZoIoFsxKFt9afv4rDs	2025-09-22 22:42:33.0987+00	2025-09-15 22:42:33.092189+00	\N	\N	f
224	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk5MzA1Mi43Mzc4NDYsImV4cCI6MTc1ODU5Nzg1Mi43Mzc4NDYsIm5iZiI6MTc1Nzk5MzA1Mi43Mzc4NDZ9.ajZuH_ZrIJ5AMwiRaC2l_qvVlz2lXAWlRLe5FKBu9fY	2025-09-23 03:24:12.737894+00	2025-09-16 03:24:12.722035+00	\N	\N	f
225	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1Nzk5OTc4NC4wMzM0MDEsImV4cCI6MTc1ODYwNDU4NC4wMzM0MDEsIm5iZiI6MTc1Nzk5OTc4NC4wMzM0MDF9.gI-gyuUk6Gdzvgr2b91hAdm-nBoBhGeLocH-gDT1hIs	2025-09-23 05:16:24.033461+00	2025-09-16 05:16:24.015881+00	\N	\N	f
226	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODA3MzE5OS43OTU1NTMsImV4cCI6MTc1ODY3Nzk5OS43OTU1NTMsIm5iZiI6MTc1ODA3MzE5OS43OTU1NTN9.jUgP3-gRLwAoWutVRMnWRRORReLpDk5g7BhNp9rIFzw	2025-09-24 01:39:59.795622+00	2025-09-17 01:39:59.789279+00	\N	\N	f
227	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODA3ODIwMC4xOTA3MDUsImV4cCI6MTc1ODY4MzAwMC4xOTA3MDUsIm5iZiI6MTc1ODA3ODIwMC4xOTA3MDV9.OzWwTsHaXWs_5NUCPo8dw5lJm-OwOnqLCKAyZ52VQ-o	2025-09-24 03:03:20.19075+00	2025-09-17 03:03:20.184934+00	\N	\N	f
228	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODA5NTQwNC40NTE1NDIsImV4cCI6MTc1ODcwMDIwNC40NTE1NDIsIm5iZiI6MTc1ODA5NTQwNC40NTE1NDJ9.byNB7xB60leu3mW1L1udhuORPvMnPRJLtu1vC-rHeYw	2025-09-24 07:50:04.451586+00	2025-09-17 07:50:04.445615+00	\N	\N	f
229	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODA5OTI1Ny4zOTcyNiwiZXhwIjoxNzU4NzA0MDU3LjM5NzI2LCJuYmYiOjE3NTgwOTkyNTcuMzk3MjZ9.b70TCrh0NE_aE1eB_nKRMdSPa9fR48D3ikxByL_Y260	2025-09-24 08:54:17.397339+00	2025-09-17 08:54:17.390935+00	\N	\N	f
230	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODA5OTc5Ny44NjA5MTcsImV4cCI6MTc1ODcwNDU5Ny44NjA5MTcsIm5iZiI6MTc1ODA5OTc5Ny44NjA5MTd9.upVNQJb4lLnjhz-hqw7PK3laWtRk6sOFskn9K8wVjNE	2025-09-24 09:03:17.860965+00	2025-09-17 09:03:17.844105+00	\N	\N	f
231	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODEwMjg1NS4wMjQxNzUsImV4cCI6MTc1ODcwNzY1NS4wMjQxNzUsIm5iZiI6MTc1ODEwMjg1NS4wMjQxNzV9.R4JTU6Mywx2xKjwjjJfRfvqkV35AwHty1sd9QQ7ca14	2025-09-24 09:54:15.024227+00	2025-09-17 09:54:15.008813+00	\N	\N	f
232	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODExMjUxNC4xMDcyMzYsImV4cCI6MTc1ODcxNzMxNC4xMDcyMzYsIm5iZiI6MTc1ODExMjUxNC4xMDcyMzZ9.cwpm73hMuxj99dVGW93MBv2ra6Lgx8bZuC_pFNNhiS8	2025-09-24 12:35:14.107284+00	2025-09-17 12:35:14.092153+00	\N	\N	f
233	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODExMzQ2MC4wMjE3NzgsImV4cCI6MTc1ODcxODI2MC4wMjE3NzgsIm5iZiI6MTc1ODExMzQ2MC4wMjE3Nzh9.-INSeoM-Q-5KWG3jRQAOiGOd3gpxd7WG5KxlN5A_gQc	2025-09-24 12:51:00.021846+00	2025-09-17 12:51:00.014907+00	\N	\N	f
234	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODExNDU3NC45MTYxNjcsImV4cCI6MTc1ODcxOTM3NC45MTYxNjcsIm5iZiI6MTc1ODExNDU3NC45MTYxNjd9.Ng-hIk67k9SXJVIj4ZEgHrzRr6qzwcKWC3PYnbCSPJg	2025-09-24 13:09:34.916212+00	2025-09-17 13:09:34.907407+00	\N	\N	f
235	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE0ODIwMC44NDkyNDYsImV4cCI6MTc1ODc1MzAwMC44NDkyNDYsIm5iZiI6MTc1ODE0ODIwMC44NDkyNDZ9.GlUaprwVXNDDmo4hioc2UkraQCH8EFFVGuorgOaclpk	2025-09-24 22:30:00.849295+00	2025-09-17 22:30:00.841638+00	\N	\N	f
236	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE0OTI0NS45NTg3MjQsImV4cCI6MTc1ODc1NDA0NS45NTg3MjQsIm5iZiI6MTc1ODE0OTI0NS45NTg3MjR9.W5QZFyRIcBIIEVt3QRnS20WGiEAT1qlKSTu4jAw0UgQ	2025-09-24 22:47:25.958855+00	2025-09-17 22:47:25.952935+00	\N	\N	f
237	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE2MjM4Ny4xNjMzOTYsImV4cCI6MTc1ODc2NzE4Ny4xNjMzOTYsIm5iZiI6MTc1ODE2MjM4Ny4xNjMzOTZ9.iJ7W-37S--Aqrj2YpxP2HLkMDHIcZ6Io_6exnbGCls4	2025-09-25 02:26:27.163454+00	2025-09-18 02:26:27.155693+00	\N	\N	f
238	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE2NTYzOS4wODE2NjgsImV4cCI6MTc1ODc3MDQzOS4wODE2NjgsIm5iZiI6MTc1ODE2NTYzOS4wODE2Njh9.29ep2a_klWIn7higy9sDhHTP2rNyyDXDdMCKQGQe3aw	2025-09-25 03:20:39.081716+00	2025-09-18 03:20:39.064389+00	\N	\N	f
239	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE2Njk5Ny40Mjk5MjEsImV4cCI6MTc1ODc3MTc5Ny40Mjk5MjEsIm5iZiI6MTc1ODE2Njk5Ny40Mjk5MjF9.9nMUpsh6iQHumLtdjwjkfBLe9WKObc0Qa_uUahkh36c	2025-09-25 03:43:17.429983+00	2025-09-18 03:43:17.421482+00	\N	\N	f
240	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE3MTgzMC45NTQxNDYsImV4cCI6MTc1ODc3NjYzMC45NTQxNDYsIm5iZiI6MTc1ODE3MTgzMC45NTQxNDZ9.M1lT17Ma4L0dZFwfRWX4JpihgoHki_SbYcq4mfxiKKg	2025-09-25 05:03:50.954198+00	2025-09-18 05:03:50.939401+00	\N	\N	f
241	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE3Mzc3NS43MTY3MSwiZXhwIjoxNzU4Nzc4NTc1LjcxNjcxLCJuYmYiOjE3NTgxNzM3NzUuNzE2NzF9.twsUoS4aUJHjv2TWtqIjSJKDGUvWxrI3T_roevLY3vA	2025-09-25 05:36:15.716758+00	2025-09-18 05:36:15.710342+00	\N	\N	f
242	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE3NDg2Mi43ODg2NDgsImV4cCI6MTc1ODc3OTY2Mi43ODg2NDgsIm5iZiI6MTc1ODE3NDg2Mi43ODg2NDh9.kxdqKpWzJF3xPYW6nhBaur41I1hak8XEWEZf1WgscEg	2025-09-25 05:54:22.788693+00	2025-09-18 05:54:22.782448+00	\N	\N	f
243	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE4Nzc5NS41NzQ3NzMsImV4cCI6MTc1ODc5MjU5NS41NzQ3NzMsIm5iZiI6MTc1ODE4Nzc5NS41NzQ3NzN9.AgoKs__VmiOb8CxTpueKWVghhNBa16ea86uY1IUti2o	2025-09-25 09:29:55.574824+00	2025-09-18 09:29:55.568501+00	\N	\N	f
244	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE4ODg4My4xMzE5MTksImV4cCI6MTc1ODc5MzY4My4xMzE5MTksIm5iZiI6MTc1ODE4ODg4My4xMzE5MTl9.rlQsqWkLAH2v9X7FV2phMFf-seZh4BgZsac8oPkEq7Q	2025-09-25 09:48:03.131979+00	2025-09-18 09:48:03.114456+00	\N	\N	f
245	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE4OTg3OC4wMTQ5NjksImV4cCI6MTc1ODc5NDY3OC4wMTQ5NjksIm5iZiI6MTc1ODE4OTg3OC4wMTQ5Njl9.oqYUD6tLk9SLVQ-PnqaohZfuFQF1K32WOPep6jdAznE	2025-09-25 10:04:38.01502+00	2025-09-18 10:04:38.000997+00	\N	\N	f
246	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE5MDkwNi4yNDQ5NDMsImV4cCI6MTc1ODc5NTcwNi4yNDQ5NDMsIm5iZiI6MTc1ODE5MDkwNi4yNDQ5NDN9.weSnd9UMV3ewkdcId66w3NI-eYCxRWksuAVI7cDDeEg	2025-09-25 10:21:46.24499+00	2025-09-18 10:21:46.238256+00	\N	\N	f
247	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODE5OTg5OS41NjE0MjUsImV4cCI6MTc1ODgwNDY5OS41NjE0MjUsIm5iZiI6MTc1ODE5OTg5OS41NjE0MjV9.r4kR_HPQvA38i3G3DshNVHpwWu_NiDhV0Vd8mOamHQU	2025-09-25 12:51:39.561475+00	2025-09-18 12:51:39.546314+00	\N	\N	f
248	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODIwMDkwNi4wNzE1NjYsImV4cCI6MTc1ODgwNTcwNi4wNzE1NjYsIm5iZiI6MTc1ODIwMDkwNi4wNzE1NjZ9.dPh-VJwpKyh_R2R_OnkDmWfvQ2e4kX83WGRbe4aOqr0	2025-09-25 13:08:26.071614+00	2025-09-18 13:08:26.055978+00	\N	\N	f
249	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODIwMTg3OS42NzI2MzMsImV4cCI6MTc1ODgwNjY3OS42NzI2MzMsIm5iZiI6MTc1ODIwMTg3OS42NzI2MzN9.0lA1LoRf6s1UyVUCuhuDNzksYvg89FK6IXcFBPQmaEU	2025-09-25 13:24:39.672685+00	2025-09-18 13:24:39.658503+00	\N	\N	f
250	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODIzMzY4Ny4wNDA0MzYsImV4cCI6MTc1ODgzODQ4Ny4wNDA0MzYsIm5iZiI6MTc1ODIzMzY4Ny4wNDA0MzZ9.YjJLM_ivJiCBCjC5H91IY9S6PgEnzRVErvgbsO4jL0E	2025-09-25 22:14:47.040489+00	2025-09-18 22:14:47.025257+00	\N	\N	f
251	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODIzNTQ1My43MDAwNjgsImV4cCI6MTc1ODg0MDI1My43MDAwNjgsIm5iZiI6MTc1ODIzNTQ1My43MDAwNjh9.YckTeSuh3KsVM3HOq_7hggLeXGHGDskJVFX_PMU9vqw	2025-09-25 22:44:13.700133+00	2025-09-18 22:44:13.693213+00	\N	\N	f
252	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODIzNTU0OC40OTIwOTcsImV4cCI6MTc1ODg0MDM0OC40OTIwOTcsIm5iZiI6MTc1ODIzNTU0OC40OTIwOTd9.h13gCB6sxACrlCry_2OWMjtUw6rKlHktWAmDA9phrpU	2025-09-25 22:45:48.492146+00	2025-09-18 22:45:48.488651+00	\N	\N	f
253	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODIzNTkwOC43MDg3MTQsImV4cCI6MTc1ODg0MDcwOC43MDg3MTQsIm5iZiI6MTc1ODIzNTkwOC43MDg3MTR9.qkQA32p-WR7V2_1XKp1jRkSx6Stt3CPxrNQMUUNQUPk	2025-09-25 22:51:48.708766+00	2025-09-18 22:51:48.701665+00	\N	\N	f
254	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODIzNjQ0Mi45NzcyOTksImV4cCI6MTc1ODg0MTI0Mi45NzcyOTksIm5iZiI6MTc1ODIzNjQ0Mi45NzcyOTl9.2FUfapd2D_i4vg0BeG1CvG7sLjEtRHavML0TCwMypA8	2025-09-25 23:00:42.977373+00	2025-09-18 23:00:42.966801+00	\N	\N	f
255	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI0ODAxMC41MjU1NiwiZXhwIjoxNzU4ODUyODEwLjUyNTU2LCJuYmYiOjE3NTgyNDgwMTAuNTI1NTZ9.t7v_Tyrljk7oN5ik2ZuvGBOcWHzFw43IFt8DTsHgTBg	2025-09-26 02:13:30.525609+00	2025-09-19 02:13:30.51901+00	\N	\N	f
256	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI1MDMwOS40MzE0MTUsImV4cCI6MTc1ODg1NTEwOS40MzE0MTUsIm5iZiI6MTc1ODI1MDMwOS40MzE0MTV9.I9iR6Raj50GJvAMSiJo_8-SWDj8GPBciC6ZB8tE5NqM	2025-09-26 02:51:49.431462+00	2025-09-19 02:51:49.424683+00	\N	\N	f
257	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI1MTU1Ni42MTUxMDcsImV4cCI6MTc1ODg1NjM1Ni42MTUxMDcsIm5iZiI6MTc1ODI1MTU1Ni42MTUxMDd9.Vby59JTf1G5AreZUhUwnxaeHyLKEUshmDTcjEdKqozQ	2025-09-26 03:12:36.615157+00	2025-09-19 03:12:36.59944+00	\N	\N	f
258	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI1MjczNC44Njc2MTIsImV4cCI6MTc1ODg1NzUzNC44Njc2MTIsIm5iZiI6MTc1ODI1MjczNC44Njc2MTJ9.87KDTY70KsuP9KvhGAyzEJ06rrAwD9Yun8P1NHrpBh8	2025-09-26 03:32:14.867662+00	2025-09-19 03:32:14.862001+00	\N	\N	f
259	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI1MzczNS42OTg4MjUsImV4cCI6MTc1ODg1ODUzNS42OTg4MjUsIm5iZiI6MTc1ODI1MzczNS42OTg4MjV9.9-bXY75sxQEdtIcyco0RQ5dC_IfAUKqLmWSFM-QFF3c	2025-09-26 03:48:55.698904+00	2025-09-19 03:48:55.692472+00	\N	\N	f
260	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI1NTA0Ny4zOTI0MywiZXhwIjoxNzU4ODU5ODQ3LjM5MjQzLCJuYmYiOjE3NTgyNTUwNDcuMzkyNDN9.-y4Q3bubLiyuk9jCdx0WMQN1yHggEAd-d-zjc-kGnWU	2025-09-26 04:10:47.392477+00	2025-09-19 04:10:47.3869+00	\N	\N	f
261	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI1NjI3MC4xMzM2ODYsImV4cCI6MTc1ODg2MTA3MC4xMzM2ODYsIm5iZiI6MTc1ODI1NjI3MC4xMzM2ODZ9.HddzDUDewFYH8ZY6R9CbopCJWOpS0LwqQYvPHT_X818	2025-09-26 04:31:10.133763+00	2025-09-19 04:31:10.127421+00	\N	\N	f
262	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI1OTM2OS45NjY3NDksImV4cCI6MTc1ODg2NDE2OS45NjY3NDksIm5iZiI6MTc1ODI1OTM2OS45NjY3NDl9.v-8mC0oE9xI-NlUNMsyBzM1yjBQKX6SAB6mnpeOPzgQ	2025-09-26 05:22:49.966798+00	2025-09-19 05:22:49.961604+00	\N	\N	f
263	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI2MDgwMi40MDExMjYsImV4cCI6MTc1ODg2NTYwMi40MDExMjYsIm5iZiI6MTc1ODI2MDgwMi40MDExMjZ9.woOlf-ICT7h091yd1xq4KFfef6eXMdG2Pq3K-9QpGqA	2025-09-26 05:46:42.401171+00	2025-09-19 05:46:42.396258+00	\N	\N	f
264	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI2MTkzOS42NDgzNTQsImV4cCI6MTc1ODg2NjczOS42NDgzNTQsIm5iZiI6MTc1ODI2MTkzOS42NDgzNTR9.nXibfStN9_Ab8r9M_Ci9K9zeEx8X9M4aCnH26UX8IVM	2025-09-26 06:05:39.6484+00	2025-09-19 06:05:39.642563+00	\N	\N	f
265	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI2Mjk3MS43Mjc2MDUsImV4cCI6MTc1ODg2Nzc3MS43Mjc2MDUsIm5iZiI6MTc1ODI2Mjk3MS43Mjc2MDV9.6yLPTlY4OmBTQuCeeJ6iWPtiUlnwYS4qXmshES2QziI	2025-09-26 06:22:51.727656+00	2025-09-19 06:22:51.720759+00	\N	\N	f
266	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI3Mzc2Ny45MzQxODQsImV4cCI6MTc1ODg3ODU2Ny45MzQxODQsIm5iZiI6MTc1ODI3Mzc2Ny45MzQxODR9.tbzppmo6RerPKCO2ZaTgGnY0E0_kCx9MZw_whNfWXko	2025-09-26 09:22:47.934232+00	2025-09-19 09:22:47.928428+00	\N	\N	f
267	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODI3NDk2MC43NTA1NjIsImV4cCI6MTc1ODg3OTc2MC43NTA1NjIsIm5iZiI6MTc1ODI3NDk2MC43NTA1NjJ9.YNUGy09pZQaSLEM6ewjrtx_O0agLN34vIxd1gYtLN0Y	2025-09-26 09:42:40.750643+00	2025-09-19 09:42:40.733122+00	\N	\N	f
268	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODMxNzMyNi4wOTAzNzksImV4cCI6MTc1ODkyMjEyNi4wOTAzNzksIm5iZiI6MTc1ODMxNzMyNi4wOTAzNzl9.mRoaZOAibXfSB_bYzyECse8YWIkNkaMxxoJMTKHPDgM	2025-09-26 21:28:46.090521+00	2025-09-19 21:28:46.066445+00	\N	\N	f
269	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODMyMDA3Ni44NDc3NzUsImV4cCI6MTc1ODkyNDg3Ni44NDc3NzUsIm5iZiI6MTc1ODMyMDA3Ni44NDc3NzV9.PjdIkKD-4yn3S5vgZD6X6lMIzBM-CoWa1Bwc-RYTs_M	2025-09-26 22:14:36.847829+00	2025-09-19 22:14:36.841869+00	\N	\N	f
270	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODMyMTY0Ni4yMzk5MywiZXhwIjoxNzU4OTI2NDQ2LjIzOTkzLCJuYmYiOjE3NTgzMjE2NDYuMjM5OTN9.DFdslgdJBTEnlf42T_Q6E83gPsQBpVGPgaIw7VtcYqA	2025-09-26 22:40:46.240013+00	2025-09-19 22:40:46.234259+00	\N	\N	f
271	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODMyMjU5OC4yNTIzNTEsImV4cCI6MTc1ODkyNzM5OC4yNTIzNTEsIm5iZiI6MTc1ODMyMjU5OC4yNTIzNTF9.0jdndmys0yfq5P74WUmUPVObi6684nPmmcRkZIQiVgM	2025-09-26 22:56:38.252403+00	2025-09-19 22:56:38.246647+00	\N	\N	f
272	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODM1NzU2NS4wMDU4NTIsImV4cCI6MTc1ODk2MjM2NS4wMDU4NTIsIm5iZiI6MTc1ODM1NzU2NS4wMDU4NTJ9.4OEdkh7o4_pTebuPbk_cNw5WEHg4RkcoAI8n59niNDA	2025-09-27 08:39:25.005902+00	2025-09-20 08:39:25.000222+00	\N	\N	f
273	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODM3MTMzMS4wNzM5OTksImV4cCI6MTc1ODk3NjEzMS4wNzM5OTksIm5iZiI6MTc1ODM3MTMzMS4wNzM5OTl9.tQQiFymYxJZjBy0v-1bCBi2mPNSDESfpIEtVfI7X7NM	2025-09-27 12:28:51.074051+00	2025-09-20 12:28:51.060097+00	\N	\N	f
274	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODc4MTEzMS42OTE1MzEsImV4cCI6MTc1OTM4NTkzMS42OTE1MzEsIm5iZiI6MTc1ODc4MTEzMS42OTE1MzF9.id2Uo9gWABza2QeLSAf5_faCdYHaPKbblbEckcxiuZk	2025-10-02 06:18:51.691583+00	2025-09-25 06:18:51.675116+00	\N	\N	f
275	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODc4MzIxMC4zNzUzMzcsImV4cCI6MTc1OTM4ODAxMC4zNzUzMzcsIm5iZiI6MTc1ODc4MzIxMC4zNzUzMzd9.tck9EufIfjXbcTwBcEyzH6lFK3IZEPJhmVVxuNvfUqQ	2025-10-02 06:53:30.375388+00	2025-09-25 06:53:30.369902+00	\N	\N	f
276	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODc5Mjc1OS4yNDU5OTIsImV4cCI6MTc1OTM5NzU1OS4yNDU5OTIsIm5iZiI6MTc1ODc5Mjc1OS4yNDU5OTJ9.YN357J6A6oacHtLtEBh5mG6W3_TPb3VioP0dMnkY6mU	2025-10-02 09:32:39.246037+00	2025-09-25 09:32:39.240535+00	\N	\N	f
277	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODc5NDUzNS43NDU4MiwiZXhwIjoxNzU5Mzk5MzM1Ljc0NTgyLCJuYmYiOjE3NTg3OTQ1MzUuNzQ1ODJ9.YmMyZvhO7ORwNJL345U0Q36fEAr8udiG6lABAmjRIAA	2025-10-02 10:02:15.745867+00	2025-09-25 10:02:15.740056+00	\N	\N	f
278	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODc5NTk2Mi4wNzE5NDksImV4cCI6MTc1OTQwMDc2Mi4wNzE5NDksIm5iZiI6MTc1ODc5NTk2Mi4wNzE5NDl9.sw3pJ0CLF12xU7gcgjnenGfgzLhK9YoNBm5mxbfLMzc	2025-10-02 10:26:02.071999+00	2025-09-25 10:26:02.066204+00	\N	\N	f
279	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODgzODY0Ni44MTAxMzIsImV4cCI6MTc1OTQ0MzQ0Ni44MTAxMzIsIm5iZiI6MTc1ODgzODY0Ni44MTAxMzJ9.pBG4M8kFjjc9HpGSk0cy8f34MKHmN5yr9w-sULBh_Ik	2025-10-02 22:17:26.810181+00	2025-09-25 22:17:26.803699+00	\N	\N	f
280	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg0MDAwMi4wMzI2MzQsImV4cCI6MTc1OTQ0NDgwMi4wMzI2MzQsIm5iZiI6MTc1ODg0MDAwMi4wMzI2MzR9.zmhMZzWXMFjZGbrTFb-wHUDR_pglLp_gRQC2yarHW-s	2025-10-02 22:40:02.032681+00	2025-09-25 22:40:02.026787+00	\N	\N	f
281	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg0MDk2NC43MzQ4MjYsImV4cCI6MTc1OTQ0NTc2NC43MzQ4MjYsIm5iZiI6MTc1ODg0MDk2NC43MzQ4MjZ9.4LxRxUwcAW0uy4jQgn1iAZGcR1G9E3JnCdab1r5rNGo	2025-10-02 22:56:04.734871+00	2025-09-25 22:56:04.729233+00	\N	\N	f
282	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg1OTg5Ni4yNzY4ODYsImV4cCI6MTc1OTQ2NDY5Ni4yNzY4ODYsIm5iZiI6MTc1ODg1OTg5Ni4yNzY4ODZ9.W2Ybr0pY4CrhDRfTdo6WdesEJPto2mZNqUE_upXphMw	2025-10-03 04:11:36.276931+00	2025-09-26 04:11:36.271459+00	\N	\N	f
283	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg2OTYxOC4wODU0NDgsImV4cCI6MTc1OTQ3NDQxOC4wODU0NDgsIm5iZiI6MTc1ODg2OTYxOC4wODU0NDh9.mUca1sR_FB05nFjJu6tEY3D9O0ezN9TXe4XR9A9vfZI	2025-10-03 06:53:38.085494+00	2025-09-26 06:53:38.078896+00	\N	\N	f
284	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg2OTY0NC45MDgxNjcsImV4cCI6MTc1OTQ3NDQ0NC45MDgxNjcsIm5iZiI6MTc1ODg2OTY0NC45MDgxNjd9.hPwLK4DNbTrc5i_0VTX4ZuW09xTLlEzOGM0jg-_aEKs	2025-10-03 06:54:04.908215+00	2025-09-26 06:54:04.905017+00	\N	\N	f
285	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg3MTIxOS4zMjQ4NzUsImV4cCI6MTc1OTQ3NjAxOS4zMjQ4NzUsIm5iZiI6MTc1ODg3MTIxOS4zMjQ4NzV9.Ln2GSNdjtYYsE7N-IqSHNmh-scNZFOKZn12IuFJDmGI	2025-10-03 07:20:19.324923+00	2025-09-26 07:20:19.319211+00	\N	\N	f
286	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg3MTI3Mi4wODA5MzYsImV4cCI6MTc1OTQ3NjA3Mi4wODA5MzYsIm5iZiI6MTc1ODg3MTI3Mi4wODA5MzZ9.WPNtRCd2E3vHKUwOFZ2C-ZUNdJJBBg6Y_iwem4C3JbQ	2025-10-03 07:21:12.080984+00	2025-09-26 07:21:12.077498+00	\N	\N	f
287	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg3OTM3OC4xODQ0MjQsImV4cCI6MTc1OTQ4NDE3OC4xODQ0MjQsIm5iZiI6MTc1ODg3OTM3OC4xODQ0MjR9.CpQcBqENEr8lSawnd9dob0QbvCt08ZtEery8qgsmqG0	2025-10-03 09:36:18.184471+00	2025-09-26 09:36:18.179321+00	\N	\N	f
288	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg4MDIwNS45MzM1NCwiZXhwIjoxNzU5NDg1MDA1LjkzMzU0LCJuYmYiOjE3NTg4ODAyMDUuOTMzNTR9.I2nbdI_JUO-FIJIVnuK2zeqZU8KuAC6FDdsA-oUbrEI	2025-10-03 09:50:05.93359+00	2025-09-26 09:50:05.927427+00	\N	\N	f
289	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg4MTA1MC4zNTAyNTQsImV4cCI6MTc1OTQ4NTg1MC4zNTAyNTQsIm5iZiI6MTc1ODg4MTA1MC4zNTAyNTR9.5RFMBQTL3r37V_6jytyZPNqnlHKRlq-jS701SuDXX6I	2025-10-03 10:04:10.350303+00	2025-09-26 10:04:10.343745+00	\N	\N	f
290	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1ODg4MjgyMC4zMDcxNywiZXhwIjoxNzU5NDg3NjIwLjMwNzE3LCJuYmYiOjE3NTg4ODI4MjAuMzA3MTd9.TllpJQzfqPsOCLezlEzjNUAHyUZRxngrQ1B9Cwhl14s	2025-10-03 10:33:40.307218+00	2025-09-26 10:33:40.300575+00	\N	\N	f
291	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTAxNzEwNy4yOTg5MzQsImV4cCI6MTc1OTYyMTkwNy4yOTg5MzQsIm5iZiI6MTc1OTAxNzEwNy4yOTg5MzR9.TF0OI0WdGEwh-e7Z34RY_IF11VpGZgdcmu2ALb9HSVc	2025-10-04 23:51:47.298982+00	2025-09-27 23:51:47.293117+00	\N	\N	f
292	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTA2NDkwMC43ODg3ODIsImV4cCI6MTc1OTY2OTcwMC43ODg3ODIsIm5iZiI6MTc1OTA2NDkwMC43ODg3ODJ9.3V7-kzvRlCwdGCEWorC29K59eJFuU9mgpLNzC4nlfZs	2025-10-05 13:08:20.78883+00	2025-09-28 13:08:20.78351+00	\N	\N	f
293	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIwNTg5MC45ODA4NDUsImV4cCI6MTc1OTgxMDY5MC45ODA4NDUsIm5iZiI6MTc1OTIwNTg5MC45ODA4NDV9.njLZ2vrBafgH8V4wn2XQFkJaJGva3rnHdtrt8w-1POU	2025-10-07 04:18:10.980893+00	2025-09-30 04:18:10.974523+00	\N	\N	f
294	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIwNjg3MS4zOTQ5MTYsImV4cCI6MTc1OTgxMTY3MS4zOTQ5MTYsIm5iZiI6MTc1OTIwNjg3MS4zOTQ5MTZ9.r8tAYAaXlQ0dLag8hZxHCKWIAGW9PjljjuoO4YF-Eaw	2025-10-07 04:34:31.395082+00	2025-09-30 04:34:31.386528+00	\N	\N	f
295	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIwOTc0NC4xNTI3MjYsImV4cCI6MTc1OTgxNDU0NC4xNTI3MjYsIm5iZiI6MTc1OTIwOTc0NC4xNTI3MjZ9.PRPsdN54sxsy1jhegDaTndmqumTbXfFtqmcEQfEoVRc	2025-10-07 05:22:24.152774+00	2025-09-30 05:22:24.14732+00	\N	\N	f
296	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIyMDUwMi45ODEyNDQsImV4cCI6MTc1OTgyNTMwMi45ODEyNDQsIm5iZiI6MTc1OTIyMDUwMi45ODEyNDR9.sayFuSzDFlP4PFUT-fMNWb4Wac9KkznFYUYGrXQ7X64	2025-10-07 08:21:42.9813+00	2025-09-30 08:21:42.962476+00	\N	\N	f
297	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIyMjY3Ny4xMTY0NTIsImV4cCI6MTc1OTgyNzQ3Ny4xMTY0NTIsIm5iZiI6MTc1OTIyMjY3Ny4xMTY0NTJ9.YBl5iAB_vQsWoQOAilXpR3JhBKbv0M1JvVBAxdVhaEI	2025-10-07 08:57:57.116507+00	2025-09-30 08:57:57.109102+00	\N	\N	f
298	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIyNzAyNS44MDE1MTcsImV4cCI6MTc1OTgzMTgyNS44MDE1MTcsIm5iZiI6MTc1OTIyNzAyNS44MDE1MTd9.lwymG76eYk0p-8frzfxPD2XeW35f1gcnNtwJgRDGkqI	2025-10-07 10:10:25.801561+00	2025-09-30 10:10:25.796271+00	\N	\N	f
299	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIyNzk3MC45ODUwNzgsImV4cCI6MTc1OTgzMjc3MC45ODUwNzgsIm5iZiI6MTc1OTIyNzk3MC45ODUwNzh9.uqiwNDKoVHW8FVCDrL10cDHIuPlwBtOAPjd53OuayYQ	2025-10-07 10:26:10.985143+00	2025-09-30 10:26:10.979318+00	\N	\N	f
300	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIyOTU0NC4zNjE2ODIsImV4cCI6MTc1OTgzNDM0NC4zNjE2ODIsIm5iZiI6MTc1OTIyOTU0NC4zNjE2ODJ9.e_f9kNdt-q-LdvjYiPaVhfgiQTyFgZZm1o9pWQDUp5M	2025-10-07 10:52:24.361729+00	2025-09-30 10:52:24.355265+00	\N	\N	f
301	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTIzMjA2NC41NjkyMTMsImV4cCI6MTc1OTgzNjg2NC41NjkyMTMsIm5iZiI6MTc1OTIzMjA2NC41NjkyMTN9.79hyx5gvTI_b7nuyWT6G9ROTrGq8aVZb7CJUtfWCOGg	2025-10-07 11:34:24.569262+00	2025-09-30 11:34:24.563488+00	\N	\N	f
302	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTI3MDkxNC44Njg0MzYsImV4cCI6MTc1OTg3NTcxNC44Njg0MzYsIm5iZiI6MTc1OTI3MDkxNC44Njg0MzZ9.DTeqF5MSXeMNOt4T3Pq-YwxF9UsJod9cgT_TI4JpY3o	2025-10-07 22:21:54.868483+00	2025-09-30 22:21:54.862492+00	\N	\N	f
303	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTI4ODczMC40ODg0NjgsImV4cCI6MTc1OTg5MzUzMC40ODg0NjgsIm5iZiI6MTc1OTI4ODczMC40ODg0Njh9.4H6qVhR56Z5I7y0h-gEUWBC39XX6GuwTCiem19mkxeM	2025-10-08 03:18:50.488514+00	2025-10-01 03:18:50.471872+00	\N	\N	f
304	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTI5ODYxNy43MDI5NjksImV4cCI6MTc1OTkwMzQxNy43MDI5NjksIm5iZiI6MTc1OTI5ODYxNy43MDI5Njl9.SYuEDTKX6OGKKO_QAfghOz6VdoOBg5p9J2dE0UUXZ6A	2025-10-08 06:03:37.703052+00	2025-10-01 06:03:37.696523+00	\N	\N	f
305	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTMwMTg2Ni4yMjk5ODcsImV4cCI6MTc1OTkwNjY2Ni4yMjk5ODcsIm5iZiI6MTc1OTMwMTg2Ni4yMjk5ODd9.z_Zf2kTryv38I01Z_HiFh814RhnJq8nr9EFcuBTXzeU	2025-10-08 06:57:46.230038+00	2025-10-01 06:57:46.223605+00	\N	\N	f
306	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTMwODI2Mi4zMzI2OTYsImV4cCI6MTc1OTkxMzA2Mi4zMzI2OTYsIm5iZiI6MTc1OTMwODI2Mi4zMzI2OTZ9.7Uv_sPOo1pSqPdbQcTYw-kDeMNF-Toemvt8y4_-Me-g	2025-10-08 08:44:22.332746+00	2025-10-01 08:44:22.316907+00	\N	\N	f
307	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTMxMzczNi4wNDM3MzYsImV4cCI6MTc1OTkxODUzNi4wNDM3MzYsIm5iZiI6MTc1OTMxMzczNi4wNDM3MzZ9.pBaZjnTevZi12wnMeEnNgaBK2HaTy6QuJerKXvkSKqY	2025-10-08 10:15:36.043801+00	2025-10-01 10:15:36.029731+00	\N	\N	f
308	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTMxNDcyMC43MjE2NywiZXhwIjoxNzU5OTE5NTIwLjcyMTY3LCJuYmYiOjE3NTkzMTQ3MjAuNzIxNjd9.5CfGcbyy3GWNBoBLSeWkS6MsVKnXcQjQaa0CB7fiphY	2025-10-08 10:32:00.721723+00	2025-10-01 10:32:00.715355+00	\N	\N	f
309	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTMxNTY3NS43NDcyMDQsImV4cCI6MTc1OTkyMDQ3NS43NDcyMDQsIm5iZiI6MTc1OTMxNTY3NS43NDcyMDR9.ScWm1y_itZg2bM1tquU5DLVwKc9WkGEUhtrQbkUITWA	2025-10-08 10:47:55.747248+00	2025-10-01 10:47:55.740768+00	\N	\N	f
310	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM1MjExNi45ODk2MTUsImV4cCI6MTc1OTk1NjkxNi45ODk2MTUsIm5iZiI6MTc1OTM1MjExNi45ODk2MTV9.zz_bULuYzmv2PU2AeM0rn5p1DwgPYAgPf2Q-Lo0eq9w	2025-10-08 20:55:16.989664+00	2025-10-01 20:55:16.982471+00	\N	\N	f
311	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM1MzA1OS40OTAzMDUsImV4cCI6MTc1OTk1Nzg1OS40OTAzMDUsIm5iZiI6MTc1OTM1MzA1OS40OTAzMDV9.oc4a-bqGubmfqlzgYabaOBVwe68L1wMpk8U2CiB50ks	2025-10-08 21:10:59.490354+00	2025-10-01 21:10:59.484205+00	\N	\N	f
312	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM1NjM4NS41MDIzNjcsImV4cCI6MTc1OTk2MTE4NS41MDIzNjcsIm5iZiI6MTc1OTM1NjM4NS41MDIzNjd9.q0wb9FfJtLVNEDnYiJGjM5h7WWkzLYFbRrkZjjFFjAo	2025-10-08 22:06:25.50251+00	2025-10-01 22:06:25.495861+00	\N	\N	f
313	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM1NzMzOC41NTgwNTUsImV4cCI6MTc1OTk2MjEzOC41NTgwNTUsIm5iZiI6MTc1OTM1NzMzOC41NTgwNTV9.HE1hzcmlqhyCqBCPu1J8uTkx92aPQAe4zvjsposAhR0	2025-10-08 22:22:18.558104+00	2025-10-01 22:22:18.550983+00	\N	\N	f
314	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM4Mzg2My4zNjg4MTksImV4cCI6MTc1OTk4ODY2My4zNjg4MTksIm5iZiI6MTc1OTM4Mzg2My4zNjg4MTl9.JcSB6vA_NsmIPutYiH-Z4a5dJCZAJoizrNYuXjwYhJw	2025-10-09 05:44:23.368865+00	2025-10-02 05:44:23.362525+00	\N	\N	f
315	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM4NDg4OC4yOTQ3MzYsImV4cCI6MTc1OTk4OTY4OC4yOTQ3MzYsIm5iZiI6MTc1OTM4NDg4OC4yOTQ3MzZ9.Lja8MODRlQLdL8kNxLrn01JLSGWAeUpWtTO24MVYPzg	2025-10-09 06:01:28.294887+00	2025-10-02 06:01:28.278998+00	\N	\N	f
316	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM4NTk3MS4yMTQ1NTMsImV4cCI6MTc1OTk5MDc3MS4yMTQ1NTMsIm5iZiI6MTc1OTM4NTk3MS4yMTQ1NTN9.ZMYPeLvpfN0xf4Wr-GfbAkvtz5xNqX7OcAbJpoV1CfY	2025-10-09 06:19:31.214633+00	2025-10-02 06:19:31.198434+00	\N	\N	f
317	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM4NjkzNi44MDA1MDgsImV4cCI6MTc1OTk5MTczNi44MDA1MDgsIm5iZiI6MTc1OTM4NjkzNi44MDA1MDh9.-7s6lnLRVaPba8ZLRzUfSzPDK4W1oaqtMMpWQ9uiVdk	2025-10-09 06:35:36.800558+00	2025-10-02 06:35:36.787007+00	\N	\N	f
318	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM4ODU1OC43ODUwMzgsImV4cCI6MTc1OTk5MzM1OC43ODUwMzgsIm5iZiI6MTc1OTM4ODU1OC43ODUwMzh9.wsTnfOVRDZcuaDbESLXEWOuvHNfeHtPaZEub1mZ-u6k	2025-10-09 07:02:38.785091+00	2025-10-02 07:02:38.779377+00	\N	\N	f
319	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTM4OTY3OC44MTU5NzgsImV4cCI6MTc1OTk5NDQ3OC44MTU5NzgsIm5iZiI6MTc1OTM4OTY3OC44MTU5Nzh9.pA5yxksoYPTf8YroE8VFDULHskNmWVIq6XF3Qk2TJ6E	2025-10-09 07:21:18.816024+00	2025-10-02 07:21:18.809701+00	\N	\N	f
320	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTgzMTI0My4zODYxNzgsImV4cCI6MTc2MDQzNjA0My4zODYxNzgsIm5iZiI6MTc1OTgzMTI0My4zODYxNzh9.vT6aIVlil4ZmKM0rePiVgDTIo8ft7xcxbzw3-saxyEs	2025-10-14 10:00:43.386224+00	2025-10-07 10:00:43.380569+00	\N	\N	f
321	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTgzMjM1MC4zODQwODUsImV4cCI6MTc2MDQzNzE1MC4zODQwODUsIm5iZiI6MTc1OTgzMjM1MC4zODQwODV9.eqWjXNjqVIJStfKkTpWPa17pC72SiwGl7kTfemdr5mQ	2025-10-14 10:19:10.384135+00	2025-10-07 10:19:10.378471+00	\N	\N	f
322	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTgzNDAxNi41NDU1NjgsImV4cCI6MTc2MDQzODgxNi41NDU1NjgsIm5iZiI6MTc1OTgzNDAxNi41NDU1Njh9.wQ6mZi8A8MX1ljWhSZAfTxxhlJdCULNxq4q2sl3Arvk	2025-10-14 10:46:56.545615+00	2025-10-07 10:46:56.539045+00	\N	\N	f
323	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTg3NTg3OS4wNzk3MDQsImV4cCI6MTc2MDQ4MDY3OS4wNzk3MDQsIm5iZiI6MTc1OTg3NTg3OS4wNzk3MDR9.gxoTfbBN98E-aC2jjn4Wv9g3100lkmcRwbuu9N2Vyg0	2025-10-14 22:24:39.079753+00	2025-10-07 22:24:39.059891+00	\N	\N	f
324	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTkwODM5Ny4yODM2NDcsImV4cCI6MTc2MDUxMzE5Ny4yODM2NDcsIm5iZiI6MTc1OTkwODM5Ny4yODM2NDd9.rnRgjwGVXlczBhenHFXHe6ZUMSeqCQq1eziNDaiELVQ	2025-10-15 07:26:37.283695+00	2025-10-08 07:26:37.27796+00	\N	\N	f
325	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTkwOTg2My4xMDMyNDIsImV4cCI6MTc2MDUxNDY2My4xMDMyNDIsIm5iZiI6MTc1OTkwOTg2My4xMDMyNDJ9.Kc-wRFwHBbjw6L0IgMIo8EY38Wixt5hqWxINhd-Vi5c	2025-10-15 07:51:03.103286+00	2025-10-08 07:51:03.097284+00	\N	\N	f
326	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTkxNTIzMS45NTY4MTUsImV4cCI6MTc2MDUyMDAzMS45NTY4MTUsIm5iZiI6MTc1OTkxNTIzMS45NTY4MTV9.lBQ_FX9s_9czII0JfLOd7MoDpOhWNzSoryBUKt1NQGI	2025-10-15 09:20:31.956885+00	2025-10-08 09:20:31.939693+00	\N	\N	f
327	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTkxNjczMS4zNDgyMTYsImV4cCI6MTc2MDUyMTUzMS4zNDgyMTYsIm5iZiI6MTc1OTkxNjczMS4zNDgyMTZ9.ydPWT9hBZxrCV7ycbtKiul8BFo8V8UfylobyPW9yzaA	2025-10-15 09:45:31.348309+00	2025-10-08 09:45:31.320201+00	\N	\N	f
328	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTkxNzY5Ni41NTQwMzYsImV4cCI6MTc2MDUyMjQ5Ni41NTQwMzYsIm5iZiI6MTc1OTkxNzY5Ni41NTQwMzZ9.esTOIes_g2b6G38DP9hIIeRPGrQ20zepO_AeVCx3Nm8	2025-10-15 10:01:36.554113+00	2025-10-08 10:01:36.538642+00	\N	\N	f
329	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTkxODkzMS4zNzgyMSwiZXhwIjoxNzYwNTIzNzMxLjM3ODIxLCJuYmYiOjE3NTk5MTg5MzEuMzc4MjF9.CyoMdGsubMUaMbgmkKMZlsoVxXusg6st0_AvJqWthvU	2025-10-15 10:22:11.378259+00	2025-10-08 10:22:11.364774+00	\N	\N	f
330	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk2MTg5Mi4wMDMzMDgsImV4cCI6MTc2MDU2NjY5Mi4wMDMzMDgsIm5iZiI6MTc1OTk2MTg5Mi4wMDMzMDh9.7mcENQWFvXfomt2tT9FS8kuUGlIgUnHcT0dxzSEfTH8	2025-10-15 22:18:12.003361+00	2025-10-08 22:18:11.994158+00	\N	\N	f
331	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk2Mjc5NS41MTMzMDksImV4cCI6MTc2MDU2NzU5NS41MTMzMDksIm5iZiI6MTc1OTk2Mjc5NS41MTMzMDl9.1_nwipLe_5tCcV1Z_nC0-vCmRVQfL_ohCD2OmXyvzKg	2025-10-15 22:33:15.513359+00	2025-10-08 22:33:15.491971+00	\N	\N	f
332	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk2NDA3MC44MDU2MjksImV4cCI6MTc2MDU2ODg3MC44MDU2MjksIm5iZiI6MTc1OTk2NDA3MC44MDU2Mjl9.gi_X_ocMPc2hq-qpKrd0wtTzVorUW360cfjLzWzgF9E	2025-10-15 22:54:30.805678+00	2025-10-08 22:54:30.799766+00	\N	\N	f
333	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk2NTAzNC4yMTU1NjIsImV4cCI6MTc2MDU2OTgzNC4yMTU1NjIsIm5iZiI6MTc1OTk2NTAzNC4yMTU1NjJ9.F8VuU-AnfiODSzgvx9AnGIb2LIwHtpMy4OBBsmgxH74	2025-10-15 23:10:34.215613+00	2025-10-08 23:10:34.200198+00	\N	\N	f
334	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk5MzAxNi43Mjc2MTcsImV4cCI6MTc2MDU5NzgxNi43Mjc2MTcsIm5iZiI6MTc1OTk5MzAxNi43Mjc2MTd9.jY4nyvPbsJt_2L1Hb0GjlHTVdPDQx-d_Pv5yadRXDok	2025-10-16 06:56:56.727691+00	2025-10-09 06:56:56.721501+00	\N	\N	f
335	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk5NDA0OS45OTY0ODgsImV4cCI6MTc2MDU5ODg0OS45OTY0ODgsIm5iZiI6MTc1OTk5NDA0OS45OTY0ODh9.wkxzFgwlEvJhCIVGyKV4rRUF9Daz8uKZmvzeCEoHVKE	2025-10-16 07:14:09.996536+00	2025-10-09 07:14:09.991263+00	\N	\N	f
336	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk5NDk4Mi4xODk2MzgsImV4cCI6MTc2MDU5OTc4Mi4xODk2MzgsIm5iZiI6MTc1OTk5NDk4Mi4xODk2Mzh9.St7SYTgnqDem1ex2ow-pnlM4isrbYho8OnYV_vcKISY	2025-10-16 07:29:42.189689+00	2025-10-09 07:29:42.180955+00	\N	\N	f
337	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk5NjI1My41OTQzNjQsImV4cCI6MTc2MDYwMTA1My41OTQzNjQsIm5iZiI6MTc1OTk5NjI1My41OTQzNjR9.rC0d0xYwNcWUfjfwBnktVuD34yNuPyoeyROj0sDxzIE	2025-10-16 07:50:53.594528+00	2025-10-09 07:50:53.589059+00	\N	\N	f
338	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk5NzYwOS40NDc5ODYsImV4cCI6MTc2MDYwMjQwOS40NDc5ODYsIm5iZiI6MTc1OTk5NzYwOS40NDc5ODZ9.bZl-CWeu5Uxfd35JTvc4EFIpn0ADtylueV65Gn2nqns	2025-10-16 08:13:29.448031+00	2025-10-09 08:13:29.441958+00	\N	\N	f
339	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc1OTk5OTA0Ny44NjUyMzIsImV4cCI6MTc2MDYwMzg0Ny44NjUyMzIsIm5iZiI6MTc1OTk5OTA0Ny44NjUyMzJ9.QwVgHJ7LGm_PiH9Q8-xtIa-2862rk9MF1Onj3yS1J_M	2025-10-16 08:37:27.865279+00	2025-10-09 08:37:27.859864+00	\N	\N	f
340	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDAwNjAwMS43MjM1OTQsImV4cCI6MTc2MDYxMDgwMS43MjM1OTQsIm5iZiI6MTc2MDAwNjAwMS43MjM1OTR9.gTVtt_Paa2rZBGG1wBFc2THeEfRg_34hzolv9M9pCKM	2025-10-16 10:33:21.723643+00	2025-10-09 10:33:21.718161+00	\N	\N	f
341	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDAwNzExNS43ODQxNTcsImV4cCI6MTc2MDYxMTkxNS43ODQxNTcsIm5iZiI6MTc2MDAwNzExNS43ODQxNTd9.H21c-b-uHNl_kLqWNTj-mLwMtPWQFg5nKS2MleuB1sw	2025-10-16 10:51:55.784207+00	2025-10-09 10:51:55.756722+00	\N	\N	f
342	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDA2NTQ1OC40NzEwNDMsImV4cCI6MTc2MDY3MDI1OC40NzEwNDMsIm5iZiI6MTc2MDA2NTQ1OC40NzEwNDN9.k2xg_Hx-LC_fqc55zlk5p7A1fD9gbZvcc6J-TuvmgjA	2025-10-17 03:04:18.471153+00	2025-10-10 03:04:18.463314+00	\N	\N	f
343	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDA2OTUyMC43MjA1NzgsImV4cCI6MTc2MDY3NDMyMC43MjA1NzgsIm5iZiI6MTc2MDA2OTUyMC43MjA1Nzh9.AH29wyDNk2_MWm5iqQNJh_1a2uOFTId-VTpwVsCbA98	2025-10-17 04:12:00.720657+00	2025-10-10 04:12:00.694479+00	\N	\N	f
344	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDA3MDU5MS43MDc5MzYsImV4cCI6MTc2MDY3NTM5MS43MDc5MzYsIm5iZiI6MTc2MDA3MDU5MS43MDc5MzZ9.SGIZTLzWyE3MFvBdXLSbDJcBKmxbQLUwopfkcEBecAo	2025-10-17 04:29:51.708056+00	2025-10-10 04:29:51.698175+00	\N	\N	f
345	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDA3NDk0Ni4xNzIyOTMsImV4cCI6MTc2MDY3OTc0Ni4xNzIyOTMsIm5iZiI6MTc2MDA3NDk0Ni4xNzIyOTN9.DaTUvpDdSp3n7hj-VORTt0wU12S4ElGru1jyk-LW73U	2025-10-17 05:42:26.172474+00	2025-10-10 05:42:25.924906+00	\N	\N	f
346	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDA5MDQ2NS40NDM2NzIsImV4cCI6MTc2MDY5NTI2NS40NDM2NzIsIm5iZiI6MTc2MDA5MDQ2NS40NDM2NzJ9.8RBKxLKqNSY4gHukxNElrw2MPEr4EfqJ6F-0kpQ21sE	2025-10-17 10:01:05.443722+00	2025-10-10 10:01:05.330508+00	\N	\N	f
347	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDA5MjI0MS45NzAwNTksImV4cCI6MTc2MDY5NzA0MS45NzAwNTksIm5iZiI6MTc2MDA5MjI0MS45NzAwNTl9.IVMPjq-w-5JKBZuIbzM3Bdia58_x1iRurcF8Smghx38	2025-10-17 10:30:41.970217+00	2025-10-10 10:30:41.936618+00	\N	\N	f
348	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDEwMTYxMy40MDY4MTMsImV4cCI6MTc2MDcwNjQxMy40MDY4MTMsIm5iZiI6MTc2MDEwMTYxMy40MDY4MTN9.vlDChWqCZUQakpun-zr4_Fc24ftaJO6BtPupvQn9Em8	2025-10-17 13:06:53.406898+00	2025-10-10 13:06:53.398036+00	\N	\N	f
349	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDEzMDMyMC42MjE0NiwiZXhwIjoxNzYwNzM1MTIwLjYyMTQ2LCJuYmYiOjE3NjAxMzAzMjAuNjIxNDZ9.NX5A-UNua_dUTVTPCmhZnpDB8zMYamCuXn8Ah9KaT3M	2025-10-17 21:05:20.621793+00	2025-10-10 21:05:20.607409+00	\N	\N	f
350	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDEzMTM2MC44MTAxMTksImV4cCI6MTc2MDczNjE2MC44MTAxMTksIm5iZiI6MTc2MDEzMTM2MC44MTAxMTl9.7WnPVs3VxbEe3gCCAzZ57hc5l3SYQLIemdfdgi2PDfs	2025-10-17 21:22:40.810268+00	2025-10-10 21:22:40.796546+00	\N	\N	f
351	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDE1MzE1OS43MjUxODIsImV4cCI6MTc2MDc1Nzk1OS43MjUxODIsIm5iZiI6MTc2MDE1MzE1OS43MjUxODJ9.LhdLcD5Y1NsP2CWj1VdFyo_keK6cRHWSvsMF6jDQuhs	2025-10-18 03:25:59.725285+00	2025-10-11 03:25:59.713017+00	\N	\N	f
352	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDE2MTg2NS45MDcyOTgsImV4cCI6MTc2MDc2NjY2NS45MDcyOTgsIm5iZiI6MTc2MDE2MTg2NS45MDcyOTh9.EMY3zK0etW7rLp7SB_vhJjHWBdKvh_d-0FLKSELtalw	2025-10-18 05:51:05.907369+00	2025-10-11 05:51:05.892595+00	\N	\N	f
353	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDE4NjEzNy44NTI5NjYsImV4cCI6MTc2MDc5MDkzNy44NTI5NjYsIm5iZiI6MTc2MDE4NjEzNy44NTI5NjZ9.-P7BC-xuFQfDwACMtVq8Q9kWKs8ivVfoC3XcDbq5KOI	2025-10-18 12:35:37.853419+00	2025-10-11 12:35:37.82493+00	\N	\N	f
354	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDE4NzA4MS40MDAwNjYsImV4cCI6MTc2MDc5MTg4MS40MDAwNjYsIm5iZiI6MTc2MDE4NzA4MS40MDAwNjZ9.s7LpaTFKu6oY7AVKoPJHdQ2P7bpWYqiYocnVqf-eKYo	2025-10-18 12:51:21.400147+00	2025-10-11 12:51:21.390948+00	\N	\N	f
355	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDIyMDYwOC40MjkwOTMsImV4cCI6MTc2MDgyNTQwOC40MjkwOTMsIm5iZiI6MTc2MDIyMDYwOC40MjkwOTN9.yZRYwqpIAvCDpVZ4c67915gbOGcuc67xhyUFxEkqWBI	2025-10-18 22:10:08.429268+00	2025-10-11 22:10:08.399008+00	\N	\N	f
356	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDIyNDAyMi4wOTkyNjIsImV4cCI6MTc2MDgyODgyMi4wOTkyNjIsIm5iZiI6MTc2MDIyNDAyMi4wOTkyNjJ9.aFhNvLMqmNK4pRgPHo9cEzOswmQFQpsgVfJLhgqnTxM	2025-10-18 23:07:02.099344+00	2025-10-11 23:07:02.089053+00	\N	\N	f
357	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDI2MjE1Ni43NzM3MDQsImV4cCI6MTc2MDg2Njk1Ni43NzM3MDQsIm5iZiI6MTc2MDI2MjE1Ni43NzM3MDR9.4Sw5oX9OZsK2h6KzswKG91K3LkUw85E2umRTQX9qSDU	2025-10-19 09:42:36.77394+00	2025-10-12 09:42:36.230974+00	\N	\N	f
358	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc2MDI2MzgxMC4zMjI1MDUsImV4cCI6MTc2MDg2ODYxMC4zMjI1MDUsIm5iZiI6MTc2MDI2MzgxMC4zMjI1MDV9.1WVMwLGcZL71m9iitA4wXl1OuzxlyIOglE07eDfAdzY	2025-10-19 10:10:10.322602+00	2025-10-12 10:10:10.228524+00	\N	\N	f
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, password_hash, first_name, last_name, is_active, is_verified, is_superuser, created_at, updated_at, last_login, deleted_at, failed_login_attempts, locked_until, last_failed_login) FROM stdin;
1	admin@m-erp.com	$2b$12$gNWL5RNcFxEUgSZ5N5C2EOq4ElHnrXbD77F/KWpy/gH2av.TFKnEC	System	Administrator	t	t	t	2025-08-23 04:26:22.146826+00	2025-10-12 10:10:08.597098+00	2025-10-12 10:10:09.053125+00	\N	0	\N	\N
\.


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 360, true);


--
-- Name: password_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.password_history_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 12, true);


--
-- Name: service_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_tokens_id_seq', 390, true);


--
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.services_id_seq', 4, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 2, true);


--
-- Name: user_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_sessions_id_seq', 358, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: user_roles _user_role_uc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT _user_role_uc UNIQUE (user_id, role_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: password_history password_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_history
    ADD CONSTRAINT password_history_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: service_tokens service_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_tokens
    ADD CONSTRAINT service_tokens_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_action_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_action_created ON public.audit_logs USING btree (action, created_at);


--
-- Name: idx_audit_ip_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_ip_created ON public.audit_logs USING btree (ip_address, created_at);


--
-- Name: idx_audit_severity_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_severity_created ON public.audit_logs USING btree (severity, created_at);


--
-- Name: idx_audit_success_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_success_created ON public.audit_logs USING btree (success, created_at);


--
-- Name: idx_audit_user_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_user_action ON public.audit_logs USING btree (user_id, action);


--
-- Name: idx_users_failed_attempts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_failed_attempts ON public.users USING btree (failed_login_attempts);


--
-- Name: idx_users_last_failed_login; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_last_failed_login ON public.users USING btree (last_failed_login);


--
-- Name: idx_users_locked_until; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_locked_until ON public.users USING btree (locked_until);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_endpoint; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_endpoint ON public.audit_logs USING btree (endpoint);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_audit_logs_ip_address; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_ip_address ON public.audit_logs USING btree (ip_address);


--
-- Name: ix_audit_logs_request_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_request_id ON public.audit_logs USING btree (request_id);


--
-- Name: ix_audit_logs_service_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_service_id ON public.audit_logs USING btree (service_id);


--
-- Name: ix_audit_logs_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_session_id ON public.audit_logs USING btree (session_id);


--
-- Name: ix_audit_logs_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_severity ON public.audit_logs USING btree (severity);


--
-- Name: ix_audit_logs_success; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_success ON public.audit_logs USING btree (success);


--
-- Name: ix_audit_logs_target_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_target_user_id ON public.audit_logs USING btree (target_user_id);


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_password_history_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_history_id ON public.password_history USING btree (id);


--
-- Name: ix_password_history_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_history_user_created ON public.password_history USING btree (user_id, created_at);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_service_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_tokens_id ON public.service_tokens USING btree (id);


--
-- Name: ix_service_tokens_service_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_tokens_service_id ON public.service_tokens USING btree (service_id);


--
-- Name: ix_service_tokens_token_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_service_tokens_token_hash ON public.service_tokens USING btree (token_hash);


--
-- Name: ix_services_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_services_id ON public.services USING btree (id);


--
-- Name: ix_services_service_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_services_service_name ON public.services USING btree (service_name);


--
-- Name: ix_user_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_id ON public.user_roles USING btree (id);


--
-- Name: ix_user_roles_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_role_id ON public.user_roles USING btree (role_id);


--
-- Name: ix_user_roles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_user_id ON public.user_roles USING btree (user_id);


--
-- Name: ix_user_sessions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_sessions_id ON public.user_sessions USING btree (id);


--
-- Name: ix_user_sessions_refresh_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_user_sessions_refresh_token ON public.user_sessions USING btree (refresh_token);


--
-- Name: ix_user_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_sessions_user_id ON public.user_sessions USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: password_history password_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_history
    ADD CONSTRAINT password_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict lyT7tMc4rUEd1dZIvzG4ZeP9NzTM3LveqrhfiJHmckOUUe6ZrwLGAL5ZrdeaKrE

