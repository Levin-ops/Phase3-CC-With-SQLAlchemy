from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


engine = create_engine('sqlite:///restaurant.db')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    reviews = relationship('Review', back_populates='restaurant')

    def get_reviews(self):
        return self.reviews

    def get_customers(self):
        return [review.customer for review in self.reviews]

    @classmethod
    def fanciest(cls):
        return session.query(cls).order_by(cls.price.desc()).first()

    def all_reviews(self):
        return [f"Review for {self.name} by {review.customer.full_name()}: {review.star_rating} stars."
                for review in self.reviews]


class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    reviews = relationship('Review', back_populates='customer')

    def get_reviews(self):
        return self.reviews

    def get_restaurants(self):
        return [review.restaurant for review in self.reviews]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        max_rating = max([review.star_rating for review in self.reviews])
        favorite_reviews = [review for review in self.reviews if review.star_rating == max_rating]
        return favorite_reviews[0].restaurant if favorite_reviews else None

    def add_review(self, restaurant, rating):
        new_review = Review(restaurant=restaurant, customer=self, star_rating=rating)
        session.add(new_review)
        session.commit()

    def delete_reviews(self, restaurant):
        reviews_to_delete = [review for review in self.reviews if review.restaurant == restaurant]
        for review in reviews_to_delete:
            session.delete(review)
        session.commit()




class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    star_rating = Column(Integer)
    restaurant = relationship('Restaurant', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')

    def customer(self):
        return self.customer

    def restaurant(self):
        return self.restaurant

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."


# TESTS

restaurant_1 = Restaurant(name="Kwa Mathe", price=3)
restaurant_2 = Restaurant(name="Kempinski", price=4)
customer_1 = Customer(first_name="Sultan", last_name="Mondoi")
customer_2 = Customer(first_name="Jane", last_name="Smith")

session.add_all([restaurant_1, restaurant_2, customer_1, customer_2])
session.commit()

print(restaurant_1.reviews())
print(restaurant_1.get_customers())