create table users (
     id int primary key
    ,first_name text null
    ,last_name text null
    ,username text null
    ,balance_cents int
)
;

create table payments (
     id uuid
    ,user_id int
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
    ,policy json null
    ,foreign key(user_id) references users(id)
);
