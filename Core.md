# 기본적인 Core 내용

## 1. 엔진 생성

- `engine.create_engine()`함수를 사용하여 엔진을 생성한다.
- 함수를 호출하여도 바로 커넥션이 연결되는 것이 아니라 실제 요청이 들어갈 때 연결된다(lazy 연결).
- `echo=True`를 사용하면 생성되는 SQL문을 출력한다.

  ```python
  from sqlalchemy import create_engine

  # sqlite를 사용하며, 메모리에 저장한다.
  engine = create_engine('sqlite+pysqlite:///:memory:', echo=True)
  ```

## 2. 기본 실행 명령 `execute()`

- `engine.execute()`함수를 사용하여 SQL문을 실행한다.
- `engine.execute()`함수는 `Result`객체를 반환한다.
- 일반적으로 `with engine.connect() as conn:`을 사용하여 커넥션을 생성하고, `conn.execute()`를 사용하여 SQL문을 실행한다.
- `with conn.begin() as conn:`을 사용하여 트랜잭션을 생성할 수 있으며, 정상적으로 종료되면 커밋되고, 예외가 발생하면 롤백된다.

  ```python
  from sqlalchemy import create_engine
  from sqlalchemy import text

  engine = create_engine('sqlite+pysqlite:///:memory:', echo=True)

  # 커넥션 생성
  # commit as you go 형태를 이용
  with engine.connect() as conn:
      conn.execute(text("CREATE TABLE some_table (x int, y int)"))
      conn.execute(
          text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
          [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
      )

      conn.commit()

  # 트랜잭션 생성
  # 작업이 정상적으로 완료되면 커밋, 예외가 발생하면 롤백이 자동으로 이루어짐
  with engine.begin() as conn:
      conn.execute(
          text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
          [{"x": 6, "y": 8}, {"x": 9, "y": 10}]
      )
  ```

## 3. `Result` 객체를 사용하는 fetch

- `execute()`를 통해 실행된 결과는 `Result` 객체를 반환한다.
- `for row in result:`를 사용하여 하나의 row씩 가져올 수 있다.
- `row.x`, `row.y`등 컬럼명으로 접근할 수도 있다.
- `for x, y in result:` 형태로 컬럼명을 지정하여 가져올 수도 있다.
- 결과는 `Result.all()`, `Result.one()` 등을 사용하여 가져올 수도 있다.
- `for dict_row in result.mappings():` 형형태로 `dict`와 유사한 형태로 가져올 수도 있다.

  ```python

  # tuple 형태로 접근하기
  result = conn.execute(text("select x, y from some_table"))
  for x, y in result:
      print(x, y)

  # index 형태로 접근하기
  result = conn.execute(text("select x, y from some_table"))
  for row in result:
      print(row[0], row[1])

  # 컬럼명으로 접근하기
  result = conn.execute(text("select x, y from some_table"))
  for row in result:
      print(row.x, row.y)

  # dict 형태로 접근하기
  result = conn.execute(text("select x, y from some_table"))
  for row in result.mappings():
      print(row['x'], row['y'])
  ```

## 4. 테이블 생성

- 테이블을 생성하기 위해서는 `MetaData`를 사용해야 하며, 이는 `from sqlalchemy import MetaData`에 존재한다.
- SQLAlchemy는 테이블 생성, 관리 등을 위해 `Table`, `Column`, `Integer`, `String` 등의 클래스를 제공한다.
- `metadata_obj = MetaData()` 등의 코드를 이용해 기본적인 메타데이터 객체를 생성할 수 있으며, 각 테이블에 메타데이터를 넣어준다.
- `metadata.create_all(engine)` 명령으로 MetaData()를 가지는 Table 클래스들에 대한 실제 테이블을 생성할 수 있다.

  ```python
  from sqlalchemy import create_engine
  from sqlalchemy import text
  from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

  # 엔진 생성
  engine = create_engine('sqlite+pysqlite:///:memory:', echo=True)

  # 메타데이터 객체 생성
  metadata = MetaData()

  # user 테이블 정의
  user_table = Table(
      'user',
      metadata,
      Column('id', Integer, primary_key=True),
      Column('name', String(30), nullable=False),
      Column('fullname', String)
  )

  # address 테이블 정의
  address_table = Table(
      'address',
      metadata,
      Column('id', Integer, primary_key=True),
      Column('user_id', ForeignKey('user.id'), nullable=False),
      Column('email_address', String, nullable=False)
  )

  # 테이블 생성 명령
  # metadata를 사용한 user, address 테이블이 생성된다.
  metadata.create_all(engine)
  ```

## 5. Reflection

- Reflection은 이미 존재하는 테이블의 메타데이터를 가져오는 기능이다.
- `some_table = Table("some_table", metadata_obj, autoload_with=engine)` 형태로 사용하며, 차례대로 테이블명, 메타데이터 객체, 엔진을 인자로 받는다.
- 자세한 내용은 [여기](https://docs.sqlalchemy.org/en/20/core/reflection.html)를 참고한다.

## 6. [INSERT 문](https://docs.sqlalchemy.org/en/20/tutorial/data_insert.html)

- `from sqlalchemy import insert`를 사용하여 INSERT문을 생성할 수 있다.
- `insert()`는 `Insert`객체를 반환한다.
- `stmt = insert(table).values(column1=value1, column2=value2)` 형태로 사용할 수 있다.
- `values()`에는 `dict`형태로 값을 넣을 수도 있다.
- `values([{col1: val, col2: val}, {col1: val, col2: val}])` 형식으로 여러 개의 row를 한 번에 삽입할 수도 있다.
- `conn.execute(stmt)`로 실행할 수 있으며, 작업 이후에는 당연히 커밋을 해야 반영이 된다.
- `Insert`객체를 `execute()`로 실행하면 `CursorResult`객체를 반환한다.

  ```python
  from sqlalchemy import insert

  ...

  # 단일 insert 문 작성
  with engine.connect() as conn:
      stmt = insert(user_table).values(name="kim", fullname="Anonymous, Kim")
      result = conn.execute(stmt)
      conn.commit()
      # result.lastrowid는 마지막으로 삽입된 row의 id를 반환한다.
      print(result.lastrowid)
      print(result.inserted_primary_key)  # (1,)이 반환됨

  # 다중 insert 문 작성
  with engine.connect() as conn:
      # values에 List[Dict] 형태로 값을 넣어준다.
      stmt = insert(user_table).values(
          [
              {"name": "lee", "fullname": "Unknown, Lee"},
              {"name": "park", "fullname": "Anonymous, Park"}
          ]
      )
      result = conn.execute(stmt)
      conn.commit()
      # result.lastrowid는 마지막으로 삽입된 row의 id를 반환한다.
      print(result.lastrowid)
      print(result.inserted_primary_key)  # (None,)이 반환됨

  ```

## 7. [SELECT 문](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)

- `from sqlalchemy import select`를 사용하여 SELECT문을 생성할 수 있다.
- `select()`는 `Select`객체를 반환한다.
- `select(table.c.column1, table.c.column2)` 형태로 특정 컬럼을 선택할 수 있다.

  ```python
  # 일반적인 조회
  with engine.connect() as conn:
      stmt = select(user_table).where(user_table.c.name == "Kim")
      result = conn.execute(stmt)
      for row in result:
          print(row)

  # 컬럼 선택 조회
  with engine.connect() as conn:
      stmt = select(user_table.c.name, user_table.c.fullname).where(user_table.c.name == "Kim")
      result = conn.execute(stmt)

      # mappings()를 사용하면 dict와 유사한 형태로 조회할 수 있다.
      for row_dict in result.mappings():
          print(row_dict)

  # table.c["col1", "com2"] 형태로 컬럼을 선택할 수도 있다.
  with engine.connect() as conn:
      stmt = select(user_table.c["name", "fullname"]).where(user_table.c.name == "Kim")
      result = conn.execute(stmt)

      # mappings()를 사용하면 dict와 유사한 형태로 조회할 수 있다.
      for row_dict in result.mappings():
          print(row_dict)
  ```

### 7.1. `SELECT`의 `WHERE` 절

- `.where()` 체이닝을 사용하여 조건을 추가할 수 있다.
- 파이썬 연산자를 사용해 연산하는 내용의 결과는 `True`, `False`가 아니라 표현식 객체를 반환한다.
- 2개 이상의 `where()`를 사용하면 기본적으로 `AND`로 연결된다.
- 하나의 `where()`에 여러 조건을 넣는 경우도 `AND`로 연결된다.
- `from sqlalchemy import and_, or_`를 사용하여 명시적으로 `AND`와 `OR`를 사용할 수 있다.

  ```python
  from sqlalchemy import and_, or_

  # 다중 where() 사용하는 경우
  # 기본적으로 각 where()는 AND로 연결된다.
  with engine.connect() as conn:
      stmt = select(user_table)
              .where(user_table.c.name == "Kim")
              .where(user_table.c.fullname == "Anonymous, Kim")
      result = conn.execute(stmt)
      for row in result:
          print(row)

  # 하나의 where()에 여러 조건을 넣는 경우
  # 기본적으로 where() 내의 각 조건은 AND로 연결된다.
  with engine.connect() as conn:
      stmt = select(user_table).where(
          user_table.c.name == "Kim",
          user_table.c.fullname == "Anonymous, Kim"
      )
      result = conn.execute(stmt)
      for row in result:
          print(row)

  # 명시적으로 AND와 OR를 사용하는 경우
  with engine.connect() as conn:
      stmt = select(user_table).where(
          or_(
              user_table.c.name == "Kim",
              user_table.c.fullname == "Anonymous, Kim"
          )
      )
      result = conn.execute(stmt)
      for row in result:
          print(row)
  ```

### 7.2. 명시적 FROM절과 JOIN

- 기본적으로 `select()`문은 `FROM`절을 명시하지 않아도 sqlalchemy가 알아서 추론하여 사용된다.
- 하나의 테이블만 사용하여 `select()`를 사용하는 경우에는 큰 문제가 되지 않지만, 여러 테이블을 사용하는 경우에는 `FROM`을 명시해줘야 하는 경우가 생길 수 있다.
- `join_from(left_table, right_table)`을 사용하여 명시적으로 JOIN을 사용할 수 있다.
- `select(left_table).join(right_table)`의 형태도 사용 가능하다.
- `select()`절에서 컬럼을 통해 테이블을 추론할 수 없는 경우에 `select(something).select_from(left_table).join(right_table)` 형태로 조인을 진행할 수도 있다.
- 외래키 제약조건이 존재하지 않는 조인의 경우엔 sqlalchemy가 ON절을 자동으로 추론할 수 없기 때문에, `join_from(left_table, right_table, on_clause)`, `join(right_table, on_clause)` 형태로 지정해줘야 한다.
- LEFT OUTER JOIN의 경우 `join_from(left_table, right_table, isouter=True)`, `join(right_table, isouter=True)` 형태로 지정해줘야 한다.
- FULL OUTER JOIN의 경우 `join_from(left_table, right_table, full=True)`, `join(right_table, full=True)` 형태로 지정해줘야 한다.
- 참고로 sqlalchemy는 RIGHT OUTER JOIN을 지원하지 않는다.

  ```python
  # 단일 테이블 조회
  stmt = select(user_table.c.name, user_table.c.fullname)
  print(stmt)  # SELECT "user".name, "user".fullname FROM "user"

  # 다중 테이블 기본 조회
  stmt = select(user_table.c.name, address_table.c.email_address)
  print(stmt)  # SELECT "user".name, address.email_address FROM "user", address

  # 명시적 FROM절 사용
  stmt = select(user_table.c.name, address_table.c.email_address).select_from(user_table).join(address_table)
  print(stmt)  # SELECT "user".name, address.email_address FROM "user" JOIN address ON "user".id = address.user_id

  # ON절을 명시적으로 사용
  stmt = select(user_table.c.name, address_table.c.email_address).select_from(user_table).join(address_table, user_table.c.id == address_table.c.user_id)
  print(stmt)  # SELECT "user".name, address.email_address FROM "user" JOIN address ON "user".id = address.user_id

  # LEFT OUTER JOIN 사용
  stmt = select(user_table.c.name, address_table.c.email_address).select_from(user_table).join(address_table, isouter=True)
  print(stmt)  # SELECT "user".name, address.email_address FROM "user" LEFT OUTER JOIN address ON "user".id = address.user_id

  # FULL OUTER JOIN 사용
  stmt = select(user_table.c.name, address_table.c.email_address).select_from(user_table).join(address_table, full=True)
  print(stmt)  # SELECT "user".name, address.email_address FROM "user" FULL OUTER JOIN address ON "user".id = address.user_id
  ```

### 7.3. ORDER BY

- `select().order_by(col1, col2)`를 사용하여 정렬할 수 있다.
- `table.c.col.asc()` 혹은 `table.c.col.desc()`를 사용하여 정렬 방식을 지정할 수 있다.

```python
# 단일 컬럼 정렬
stmt = select(user_table).order_by(user_table.c.name)
print(stmt)  # SELECT "user".id, "user".name, "user".fullname FROM "user" ORDER BY "user".name

# 다중 컬럼 정렬
stmt = select(user_table).order_by(user_table.c.name, user_table.c.fullname)
print(stmt)  # SELECT "user".id, "user".name, "user".fullname FROM "user" ORDER BY "user".name, "user".fullname

# 정렬 방식 지정
stmt = select(user_table).order_by(user_table.c.name.asc(), user_table.c.fullname.desc())
print(stmt)  # SELECT "user".id, "user".name, "user".fullname FROM "user" ORDER BY "user".name ASC, "user".fullname DESC
```

### 7.4. GROUP BY, HAVING

- `select().group_by(col1, col2)`를 사용하여 그룹화할 수 있다.
- `group_by().having()`을 사용하여 그룹화된 결과에 조건을 추가할 수 있다.
- 일반적으로 having절은 집계함수를 사용하는데, 이를 위해 sqlalchemy는 `from sqlalchemy import func`를 제공하며, `func.count()`, `func.sum()`, `func.avg()` 등을 사용할 수 있다.

  ```python
  from sqlalchemy import func

  # 단일 컬럼 그룹화
  stmt = select(user_table.c.name, func.count(address_table.c.id)).select_from(user_table).join(address_table).group_by(user_table.c.name)
  print(stmt)  # SELECT "user".name, count(address.id) AS count_1 FROM "user" JOIN address ON "user".id = address.user_id GROUP BY "user".name

  # 다중 컬럼 그룹화
  stmt = select(user_table.c.name, user_table.c.fullname, func.count(address_table.c.id)).select_from(user_table).join(address_table).group_by(user_table.c.name, user_table.c.fullname)
  print(stmt)  # SELECT "user".name, "user".fullname, count(address.id) AS count_1 FROM "user" JOIN address ON "user".id = address.user_id GROUP BY "user".name, "user".fullname

  # 그룹화된 결과에 조건 추가
  stmt = select(user_table.c.name, func.count(address_table.c.id)).select_from(user_table).join(address_table).group_by(user_table.c.name).having(func.count(address_table.c.id) > 1)
  print(stmt)  # SELECT "user".name, count(address.id) AS count_1 FROM "user" JOIN address ON "user".id = address.user_id GROUP BY "user".name HAVING count(address.id) > :count_1
  ```

### 7.5. Subquery, CTEs

- `.subquery()`를 사용하여 서브쿼리를 사용할 수 있다.
- `.cte()`를 사용하여 CTEs를 사용할 수 있다.
- 자세한 내용은 [여기](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#subqueries-and-ctes)를 참고한다.

## 8. [UPDATE 및 DELETE 문](https://docs.sqlalchemy.org/en/20/tutorial/data_update.html)

- `from sqlalchemy import update, delete`를 사용하여 UPDATE 및 DELETE문을 생성할 수 있다.
- `update(table).where(condition).values(col1=value1, col2=value2)` 형태로 사용할 수 있다.
- `delete(table).where(condition)` 형태로 사용할 수 있다.
- update 및 delete로 반영된 row수를 결과로 받을 수 있다.

```python
from sqlalchemy import update, delete

# UPDATE
with engine.connect() as conn:
    stmt = update(user_table).where(user_table.c.name == "kim").values(fullname="Anonymous, Kim")

    print(stmt)  # UPDATE "user" SET fullname=:fullname WHERE "user".name = :name_1

    result = conn.execute(stmt)
    conn.commit()
    print(result.rowcount)  # 1

# DELETE
with engine.connect() as conn:
    stmt = delete(user_table).where(user_table.c.name == "kim")

    print(stmt)  # DELETE FROM "user" WHERE "user".name = :name_1

    result = conn.execute(stmt)
    conn.commit()
    print(result.rowcount)  # 1

```
