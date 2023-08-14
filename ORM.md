# ORM

## 1. 기본적인 ORM 사용법

- ORM도 기본적으로 engine을 사용하는 것은 동일하다.
- ORM은 `from sqlalchemy.orm import Session`을 통해 사용하며, `with Session(engine) as session:`을 통해 session을 사용한다.
- session을 사용하면, `session.add()`, `session.commit()`, `session.rollback()` 등을 사용할 수 있다.
- session 내에서 ORM 객체를 사용하는 것이 아니라면, 기존 Connection 객체를 사용하는 것과 동일하다.

  ```python
  from sqlalchemy.orm import Session  # ORM 세션을 사용하기 위해 import

  # 쿼리 등을 펺하게 관리하기 위해 stmt로 분리
  stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")

  # Session을 사용
  with Session(engine) as session:
      result = session.execute(stmt, {"y": 6})
      for row in result:
          print(f"x: {row.x}  y: {row.y}")
  ```

## 2. 테이블 객체 생성

- Core처럼 ORM도 메타데이터를 사용하여 테이블 객체를 생성한다.
- ORM에서는 `from sqlalchemy.orm import DeclarativeBase` 클래스를 상속한 클래스를 사용한다.
- 이후 생성할 클래스는 위에서 생성한 클래스를 상속받아 작성한다.
- 2.0부터는 선언형 테이블을 사용하기 때문에, 컬럼 타입을 사용할 때 Mapped[type] = mapped_column(type)을 사용한다.
- 테이블간의 관계는 `relationship()`을 사용하여 정의하며, 자세한 내용은 [여기](https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html#tutorial-orm-related-objects)를 참고한다.
- 마지막으로 `Base.metadata.create_all(engine)` 명령으로 테이블을 생성할 수 있다.

  ```python
  from typing import List, Optional

  from sqlalchemy import create_engine
  from sqlalchemy import String, ForeignKey
  from sqlalchemy.orm import DeclarativeBase
  from sqlalchemy.orm import Mapped, mapped_column
  from sqlalchemy.orm import relationship


  # 엔진 생성
  engine = create_engine('sqlite+pysqlite:///:memory:', echo=True)

  # DeclarativeBase를 상속받아 기본 클래스를 생성
  class Base(DeclarativeBase):
      pass

  # user_account 테이블을 위한 클래스
  class User(Base):
      # 테이블 이름을 명시
      __tablename__ = "user_account"
      # 사용할 컬럼을 명시
      # Mapped[type] = mapped_column(type)을 사용하여 컬럼 타입을 명시
      id: Mapped[int] = mapped_column(primary_key=True)
      name: Mapped[str] = mapped_column(String(30))
      fullname: Mapped[Optional[str]]
      addresses: Mapped[List["Address"]] = relationship(back_populates="user")
      # __repr__을 사용하여 객체를 출력할 때 사용할 문자열을 정의
      def __repr__(self) -> str:
          return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

  # address 테이블을 위한 클래스
  class Address(Base):
      __tablename__ = "address"
      id: Mapped[int] = mapped_column(primary_key=True)
      email_address: Mapped[str]
      user_id = mapped_column(ForeignKey("user_account.id"))
      user: Mapped[User] = relationship(back_populates="addresses")
      def __repr__(self) -> str:
          return f"Address(id={self.id!r}, email_address={self.email_address!r})"

  # 테이블 생성
  Base.metadata.create_all(engine)
  ```
