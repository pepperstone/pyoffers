# coding: utf-8
from pyoffers.utils import Filter, Sort
from .core import InvisibleModelManager, Model, ModelManager
from .offer_file import OfferFileManager


class AffiliateOffer(Model):
    """
    Model that defines relation between Offer and Affiliate
    """
    display_attribute = 'approval_status'


class AffiliateOfferManager(InvisibleModelManager):
    model = AffiliateOffer


class AffiliateUser(Model):
    generic_methods = ()


class AffiliateUserManager(ModelManager):
    model = AffiliateUser
    name = 'affiliate_users'
    generic_methods = (
        'create',
        'update',
        'delete',
        'find_by_id',
        'find_all',
        'find_all_ids',
    )


class AffiliateBilling(Model):
    pass


class AffiliateInvoice(Model):
    pass


class AffiliateBillingManager(ModelManager):
    model = AffiliateBilling
    model_aliases = ["AffiliateInvoice"]
    name = 'affiliate_billings'
    generic_methods = ()

    def find_all(self, sort=(), limit=None, page=None, fields=None, contain=None, **kwargs):
        assert limit is None or isinstance(limit, int), 'Limit should be an integer'
        assert page is None or isinstance(page, int), 'Page should be an integer'
        assert fields is None or isinstance(fields, (tuple, list)), 'Fields should be a tuple or list'
        return self._call(
            'findAllInvoices',
            filters=Filter(**kwargs),
            sort=Sort(sort, self.model.__name__),
            limit=limit, page=page, fields=fields, contain=contain, single_result=False
        )


class Affiliate(Model):
    """
    An Affiliate.
    """
    generic_methods = ('update', 'delete')

    @property
    def user(self):
        try:
            return AffiliateUserManager(self._manager.api).find_all(affiliate_id=self.id)[0]
        except IndexError:
            return None

    @property
    def files(self):
        return self._get_related_manager(OfferFileManager, 'account_id')

    def block(self, reason=None):
        return self._manager.block(self.id, reason=reason)

    def get_offer_files_with_creative_code(self, offer_id):
        return self._manager.get_offer_files_with_creative_code(self.id, offer_id)


class AffiliateManager(ModelManager):
    model = Affiliate
    name = 'affiliates'
    generic_methods = (
        'update',
        'delete',
        'find_by_id',
        'find_all',
        'find_all_ids',
    )

    def create(self, **kwargs):
        """
        Creates an affiliate
        :param kwargs:
        :return: affiliate instance
        """
        return self._call('create', data=kwargs)

    def create_with_user(self, user_params, **kwargs):
        """
        Creates an affiliate and corresponding affiliate user
        :param user_params: kwargs for user creation
        :param kwargs:
        :return: affiliate instance
        """
        affiliate = self.create(**kwargs)
        self.api.affiliate_users.create(affiliate_id=affiliate.id, **user_params)
        return affiliate

    def block(self, id, reason=None):
        return self._call('block', id=id, reason=reason)

    def get_offer_files_with_creative_code(self, id, offer_id):
        return self._call(
            'getOfferFilesWithCreativeCode',
            target='Offer', target_class='OfferFile', affiliate_id=id, offer_id=offer_id, single_result=False
        )
