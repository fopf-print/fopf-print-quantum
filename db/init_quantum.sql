create table users (
     id bigint primary key
    ,first_name text null
    ,last_name text null
    ,username text null
    ,balance_cents int
)
;

create table payments_log (
     id uuid
    ,user_id bigint
    ,amount_cents int
    ,is_confirmed boolean
    ,transaction_dttm timestamp without time zone
    ,foreign key(user_id) references users(id)
)
;

create table printing_tasks (
     id uuid
    ,user_id int
    ,message_id int
    ,file_id text
    ,status text
    ,created_dt timestamp with time zone default (now() at timestamp 'utc')
    ,updated_dt timestamp with time zone default (now() at timestamp 'utc')
    ,policy json null
    ,foreign key(user_id) references users(id)
);
