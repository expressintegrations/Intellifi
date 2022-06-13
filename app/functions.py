from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from fastapi import Depends

from .containers import Container
from .models import HubSpotCompanySyncRequest
from .services import EmergeService, HubSpotService


@inject
def sync_emerge_company_to_hubspot(
  hubspot_company_sync_request: HubSpotCompanySyncRequest,
  emerge_service: EmergeService = Depends(Provide[Container.emerge_service]),
  hubspot_service: HubSpotService = Depends(Provide[Container.hubspot_service])
):

  emerge_company = emerge_service.get_customer_billing_info(
    company_id=hubspot_company_sync_request.emerge_company_id,
    year=hubspot_company_sync_request.year,
    month=hubspot_company_sync_request.month
  )
  hubspot_service.update_company(
    company_id=hubspot_company_sync_request.object_id,
    properties=emerge_company.to_hubspot_company()
  )

@inject
def get_emerge_company(
  hubspot_company_sync_request: HubSpotCompanySyncRequest,
  emerge_service: EmergeService = Depends(Provide[Container.emerge_service])
):
  return emerge_service.get_customer_billing_info(
    company_id=hubspot_company_sync_request.emerge_company_id,
    year=hubspot_company_sync_request.year,
    month=hubspot_company_sync_request.month
  )

@inject
def sync_emerge_companies_to_hubspot(
  emerge_service: EmergeService = Depends(Provide[Container.emerge_service]),
  hubspot_service: HubSpotService = Depends(Provide[Container.hubspot_service])
):
  for customer in emerge_service.get_all_customers():
    companies = hubspot_service.get_company_by_emerge_company(emerge_company_id=customer.company_id)
    print(f"Companies search result for {customer.company_id}: {companies}")
    if companies['total'] == 0:
      # do nothing for now
      print(f"No Company found in HubSpot with Emerge Company ID {customer.company_id}")
    elif companies['total'] == 1:
      company = companies['results'][0]
      # update
      print(f"Updating company {company['id']}")
      result = sync_emerge_company_to_hubspot(
        hubspot_company_sync_request=HubSpotCompanySyncRequest(
          object_id =company['id'],
          emerge_company_id=customer.company_id
        )
      )
    else:
      # This should never happen
      raise Exception(
        f"Multiple companies found with Emerge Company ID {customer.company_id}: {companies}"
      )
