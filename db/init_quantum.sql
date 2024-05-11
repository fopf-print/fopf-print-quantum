create table users (
     id bigint primary key
    ,username text not null
    ,first_name text default null
    ,last_name text default null
    ,balance_cents int default 0
    ,created_dttm timestamp with time zone default (now() at time zone 'Europe/Moscow')
    ,is_active boolean default false
    ,activated_dttm timestamp with time zone default null
    ,role text default null
)
;

create table payments (
     id uuid primary key
    ,yookassa_id uuid default null
    ,user_id bigint
    ,amount_cents int
    ,description text not null
    ,is_confirmed boolean
    ,transaction_dttm timestamp with time zone default (now() at time zone 'Europe/Moscow')
    ,foreign key(user_id) references users(id)
)
;

create table printing_tasks (
     id uuid primary key
    ,file_id text not null
    ,user_id int
    ,message_id int
    ,cost_cents int
    ,status text
    ,parameters jsonb default null
    ,created_dttm timestamp with time zone default (now() at time zone 'Europe/Moscow')
    ,updated_dttm timestamp with time zone default (now() at time zone 'Europe/Moscow')
    ,foreign key(user_id) references users(id)
)
;
