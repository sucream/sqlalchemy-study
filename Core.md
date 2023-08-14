# 기본적인 내용

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
  from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

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
