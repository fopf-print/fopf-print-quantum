create table if not exists users (
     id int primary key
    ,first_name text null
    ,last_name text null
    ,username text null
    ,balance_cents int
)
;


create table if not exists payments (
     id text -- не верь, это uuid4
    ,user_id int
    ,amount_cents int
    ,is_confirmed boolean
    ,transaction_dttm text -- не верь, это timestamp
    ,foreign key(user_id) references users(id)
)
;
