---
name: azure-icons
description: Search and fetch official Microsoft Azure and Fabric SVG icons for use in diagrams, documentation, and UI. Covers 687 icons across compute, networking, storage, databases, AI/ML, security, identity, containers, DevOps, analytics, IoT, integration, monitoring, migration, and Microsoft Fabric workloads. Use when building architecture diagrams (HTML, PPTX, or any visual format) that need Azure or Fabric icons, or when the user asks for Microsoft cloud service icons.
---

# Azure Icons

687 official Microsoft Azure and Fabric SVG icons with metadata, covering all major Azure service categories.

## Finding Icons

Run the search script instead of reading the full index (saves context):

```bash
python3 scripts/search_icons.py "<query>" [limit]
```

Examples:
```bash
python3 scripts/search_icons.py "cosmos db"
python3 scripts/search_icons.py "virtual machine" 5
python3 scripts/search_icons.py "key vault"
python3 scripts/search_icons.py "lakehouse"
python3 scripts/search_icons.py "kubernetes"
```

Returns matching icons as JSON with `id`, `name`, `description`, `tags`, and `url`. Use the `url` field directly as an image source.

For bulk operations or browsing all icons, read `references/index.json`.

### Index Entry Format

```json
{
  "id": "azure_cosmos_db",
  "name": "Azure Cosmos Db",
  "description": "Azure Azure Cosmos Db (databases)",
  "tags": ["azure", "cosmos", "db"],
  "filename": "azure_cosmos_db_48_color.svg",
  "url": "https://raw.githubusercontent.com/AlahmadiQ8/icons/main/icons/azure_cosmos_db_48_color.svg"
}
```

## Using Icons in HTML Diagrams

```html
<img src="https://raw.githubusercontent.com/AlahmadiQ8/icons/main/icons/azure_cosmos_db_48_color.svg"
     alt="Azure Cosmos DB" width="48" height="48" />
```

## Using Icons in PPTX

Download the SVG from the `url` and add it as a picture:

```python
from pptx import Presentation
from pptx.util import Inches
import urllib.request, tempfile, os

url = "https://raw.githubusercontent.com/AlahmadiQ8/icons/main/icons/azure_cosmos_db_48_color.svg"
tmp = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
urllib.request.urlretrieve(url, tmp.name)

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.shapes.add_picture(tmp.name, Inches(1), Inches(1), Inches(1), Inches(1))
os.unlink(tmp.name)
```

## Icon Categories

**Compute:** `virtual_machines`, `virtual_machine_scale_sets`, `azure_compute_galleries`, `function_apps`, `batch_accounts`, `cloud_services_classic`

**Networking:** `virtual_networks`, `load_balancers`, `application_gateways`, `dns_zones`, `front_doors`, `expressroute_circuits`, `nat_gateways`

**Storage:** `storage_accounts`, `azure_container_storage`, `managed_disks`, `one_lake`

**Databases:** `azure_cosmos_db`, `sql_server`, `azure_database_mariadb_server`, `azure_data_explorer_clusters`, `data_warehouse`, `sql_database`, `lakehouse`

**AI + ML:** `ai_studio`, `azure_applied_ai_services`, `machine_learning`, `cognitive_services`, `anomaly_detector`, `ai_skills`

**Containers:** `kubernetes_services`, `container_instances`, `container_registries`, `aks_automatic`

**Security:** `defender_for_cloud`, `key_vaults`, `microsoft_sentinel`, `entra_id`

**Identity:** `active_directory_connect_health`, `entra_domain_services`, `entra_identity_governance`, `administrative_units`

**DevOps:** `devops`, `azure_chaos_studio`, `app_configuration`

**Analytics:** `analysis_services`, `synapse_analytics`, `power_bi`, `data_factories`, `event_hubs`

**Fabric:** `fabric`, `lakehouse`, `data_warehouse`, `pipeline`, `notebook`, `dataflow_gen2`, `eventstream`, `event_house`, `kql_database`, `semantic_model`, `copilot`

**IoT:** `iot_hub`, `iot_edge`, `digital_twins`, `sphere`

**Monitor:** `monitor`, `log_analytics_workspaces`, `application_insights`, `alerts`

**Integration:** `api_management_services`, `logic_apps`, `service_bus`, `event_grid`
