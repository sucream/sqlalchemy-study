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