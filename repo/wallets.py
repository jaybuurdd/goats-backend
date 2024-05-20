from sqlalchemy.sql.expression import or_

from models.models import GoatsByWallet
from schemas.wallets import OwnedGoats
from utils.logging import logger

class WalletRepo:
    @classmethod
    def placeholder(cls):
        return
    
class GoatsRepo:
    @classmethod
    def search_goat_owner_wallet(cls, id, db):
        try:
            logger.info("Verifying membership...")
            member = cls.search_by_goat_id(id, db)
            if member:
                all_goat_ids = []
                for m in member:
                    all_goat_ids.extend(m.GOAT_ids.split(','))

                all_goat_ids = [goat_id.strip() for goat_id in all_goat_ids]

                logger.info("Succesfully retrieved membership...")
                return OwnedGoats(
                    wallet=member[0].wallet,
                    owned_goats=all_goat_ids
                )
            else:
                logger.info("Succes: Goat id was not valid...")
                return "Goat not found"
        except Exception as e:
            logger.error(f"Error searching for owner wallet: {e}")



    @classmethod
    def search_by_goat_id(cls, id, db):
        goat_id = str(id)

        # patterns for matching
        pattern_start = goat_id + ',%'
        pattern_middle = '%,' + goat_id + ',%'
        pattern_end = '%,' + goat_id
        pattern_only = goat_id

        # perform query using LIKE operator w/ the set patterns
        member = db.query(GoatsByWallet).filter(
            or_(
                GoatsByWallet.GOAT_ids.like(pattern_start),
                GoatsByWallet.GOAT_ids.like(pattern_middle),
                GoatsByWallet.GOAT_ids.like(pattern_end),
                GoatsByWallet.GOAT_ids == pattern_only
            )
        ).all()

        return member