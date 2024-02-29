from models.models import Person, Wallet, Address
from schemas.users import Account
from utils.logging import logger


class UserRepo:
    @classmethod
    def access_google_auth(cls, user_info, db):
        logger.info("\nValidating user decoded Google Sign-in data\n")
        account = None
        try:
            user = db.query(Person).filter(Person.email == user_info['email']).first()

            if user:
                logger.info("\nLogging in existing user\n")
                wallet = db.query(Wallet).filter(Wallet.people_id == user.id).first()

                account = Account (
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                wallet=wallet.wallet if wallet else None
            )
            else:
                try:
                    logger.info("\nSigning up a new user\n")
                    #TODO: save new user into db
                    person = Person(
                        first_name=user_info['first_name'],
                        last_name=user_info['last_name'],
                        email=user_info['email'],
                        role='User'
                    )

                    db.add(person)
                    db.commit()
                    db.refresh(person)

                    return Account(
                        email=person.email,
                        first_name=person.first_name,
                        last_name=person.last_name,
                        wallet=None
                    )
                except Exception as e:
                    db.rollback() 
                    logger.error(f"Issue registering user: {e}")
                    raise e 
                
            return account
        except Exception as e:
            logger.error(f"Issue authenticating user: {e}")
            raise Exception
    

    @classmethod
    def reigster_user(cls, user_data: dict, db):
        try:
            logger.info("Registering users info")
            # check if person exists already
            person = db.query(Person).filter(Person.email == user_data['email']).first()
            
            # if doesn't exist
            # if not person:
            #     # add new user
            #     person = Person(
            #         first_name=user_data['first_name'],
            #         last_name=user_data['last_name'],
            #         email=user_data['email'],
            #         role='User'
            #     )
            #     db.add(person)
            #     db.commit()
            #     db.refresh(person) # refresh to get new person id
            if person:
                wallet = db.query(Wallet).filter(Wallet.wallet == user_data['wallet']).first()
                # if wallet exists
                if wallet: 
                    wallet.people_id = person.id
                else:
                    new_wallet = Wallet(
                        wallet=user_data['wallet'],
                        people_id=person.id,
                        type='HUMAN'
                    )    
                    db.add(new_wallet)

                address = Address(
                    people_id=person.id,
                    address1=user_data['address'],
                    city=user_data['city'],
                    state=user_data['state'],
                    postal_code=user_data['postal_code'],
                    address_type='Home',
                    country='USA'
                )

                db.add(address)

        
                db.commit()
                return
         
        except Exception as e:
            db.rollback() 
            logger.error(f"Issue registering user: {e}")
            raise e 
