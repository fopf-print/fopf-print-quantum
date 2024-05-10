create table users (
     id bigint primary key
    ,username text not null
    ,first_name text default null
    ,last_name text default null
    ,balance_cents int default 0
    ,created_dttm timestamp with time zone default (now() at time zone 'utc')
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
    ,transaction_dttm timestamp with time zone default (now() at time zone 'utc')
    ,foreign key(user_id) references users(id)
)
;
