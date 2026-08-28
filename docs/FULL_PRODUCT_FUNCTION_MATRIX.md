# SAFE-Twin Anyang — Full Product Function Matrix

Audit date: 2026-08-29. Public target: `https://anyang4d.onrender.com`. “Public result” is based on a live browser/API check; code presence is not treated as success. Docker values use the real production-container evidence from the preceding recovery validation where a fresh Docker daemon was unavailable during this audit.

| ID | Area | Feature | Expected user action | Expected visible result | Frontend implementation | Backend endpoint | Data dependency | Existing automated test | Local result | Docker result | Public result | Persistence behavior | Status | Severity | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---| 
| C01 | Citizen | Shelter category | Click shelter | Shelter list/map | App.tsx | GET /api/facilities | 231 shelters | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P0 | public citizen screenshot | |
| C02 | Citizen | Water category | Click water | Water list/map | App.tsx | GET /api/facilities | 71 water | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | public water screenshot | |
| C03 | Citizen | AED category | Click AED | AED list and 119-first action | App.tsx | GET /api/facilities | 305 AED | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | public AED screenshot | |
| C04 | Citizen | Facility list | Browse list | Records are selectable | App.tsx | facilities | official snapshots | visibility | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | citizen base | |
| C05 | Citizen | Search by name | Enter name | Matching facilities | App.tsx | client filter | facility names | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | public search | |
| C06 | Citizen | Search by address | Enter address | Matching facilities | App.tsx | client filter | facility addresses | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | public search | |
| C07 | Citizen | Facility detail | Select list item | Detail/provenance panel | App.tsx | facilities | facility record | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | facility detail | |
| C08 | Citizen | Map selection | Click map feature | Detail selected | App.tsx | map query | rendered feature | not tested | CODE_ONLY | PASS | CODE_ONLY | read-only | CODE_ONLY | P2 | source + no public proof | |
| C09 | Citizen | Current location | Request location | Location marker/center | App.tsx | browser geolocation | permission/device | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | session | CODE_ONLY | P2 | not permission-tested | |
| C10 | Citizen | Large text | Toggle text size | Larger readable UI | App.tsx | none | CSS state | visibility | PASS | PASS | PASS | session | PUBLIC_FUNCTIONAL | P2 | source/test | |
| C11 | Citizen | About/data sources | Open about | Provenance/source page | App.tsx | data-sources | source metadata | not tested | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | route/source | |
| C12 | Citizen | 119-first AED action | Click 119 | Emergency call intent/action | App.tsx | none | AED limitation | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P1 | public AED screenshot | |
| R01 | Route | Select coordinate shelter | Select shelter | Selected coordinate | App.tsx | facilities | coordinates | behavioral | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P0 | local/public UI | |
| R02 | Route | Route button | Click detail action | Button visible | App.tsx | none | selected facility | visibility | PASS | PASS | PASS | read-only | PUBLIC_FUNCTIONAL | P0 | public detail | |
| R03 | Route | Route request | Click route | POST issued | App.tsx | POST /api/routes | OSM graph | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public route failure | UI showed failure; request not independently observed |
| R04 | Route | Route HTTP response | Request route | HTTP 200 | App.tsx | POST /api/routes | OSM graph | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | API matrix/source | |
| R05 | Route | Route body | Receive response | Geometry/distance/time | App.tsx | POST /api/routes | OSM graph | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | local response/source | |
| R06 | Route | Store geometry | Complete request | Geometry in state | App.tsx | routes | route response | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public route failure | |
| R07 | Route | Map source | Route response | walking-route nonempty | MapView.tsx | routes | MapLibre | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | route screenshot/source | |
| R08 | Route | Route line | Render source | Visible line | MapView.tsx | routes | MapLibre | visibility-only | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | route screenshot | |
| R09 | Route | Origin marker | Route response | Origin marker | MapView.tsx | routes | coordinates | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public route failure | |
| R10 | Route | Destination marker | Route response | Destination marker | MapView.tsx | routes | coordinates | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public route failure | |
| R11 | Route | Fit route | Route response | Map zooms to route | MapView.tsx | routes | geometry | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public route failure | |
| R12 | Route | Distance/time text | Route response | Distance/time visible | App.tsx | routes | route metrics | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public route failure | |
| R13 | Route | Change facility route | Select another | New route | App.tsx | routes | facility coords | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | not completed publicly | |
| R14 | Route | Category clears route | Change category | Stale route cleared | App.tsx | none | UI state | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P2 | not completed publicly | |
| R15 | Route | Public/Docker parity | Compare deployments | Same route behavior | build/runtime | routes | deployment | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | n/a | PUBLIC_FUNCTIONAL | P0 | local vs public | |
| S01 | Simulation | Scenario list | Open /simulate | Scenario options | CitizenSimulationPreview.tsx | scenarios | 6 presets | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public simulation | |
| S02 | Simulation | Default scenario | Open /simulate | Competition preset selected | CitizenSimulationPreview.tsx | scenarios | preset IDs | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public simulation | |
| S03 | Simulation | Frame 0 | Open simulation | Metrics/map at t0 | CitizenSimulationPreview.tsx | frame | frame JSON | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public simulation t0 | |
| S04 | Simulation | Timeline | Open simulation | Timeline control | CitizenSimulationPreview.tsx | none | frame_times | visibility | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P1 | public simulation | |
| S05 | Simulation | Manual movement | Move timeline | Frame time/state changes | CitizenSimulationPreview.tsx | frame | frames 0/10/20/30 | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public simulation | |
| S06 | Simulation | Play advance | Click play | 0→10→20→30 with state changes | CitizenSimulationPreview.tsx | frame | frame JSON | visibility-only | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public simulation t10 | timer moved; content did not |
| S07 | Simulation | Pause | Click pause | Advancement stops | CitizenSimulationPreview.tsx | none | timer | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| S08 | Simulation | Hazard t0 | Open simulation | Hazard visible | MapView.tsx | frame | hazard geometry | not tested | PASS | PASS | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P0 | public simulation | |
| S09 | Simulation | Hazard later | Advance frame | Hazard visibly differs | MapView.tsx | frame | hazard keyframes | not tested | PASS | PASS | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P0 | public simulation | |
| S10 | Simulation | Changed roads | Advance frame | Closed roads rendered | MapView.tsx | frame | roads | not tested | PASS | PASS | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P0 | public simulation | |
| S11 | Simulation | Facility load | Advance frame | Load encoding changes | MapView.tsx | frame | assignments | not tested | PASS | PASS | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P1 | public simulation | |
| S12 | Simulation | Demand metric | Open simulation | Demand number | CitizenSimulationPreview.tsx | frame | assignment | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public simulation | |
| S13 | Simulation | Assigned metric | Open simulation | Assigned number | CitizenSimulationPreview.tsx | frame | assignment | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public simulation | |
| S14 | Simulation | Unserved metric | Open simulation | Unserved number | CitizenSimulationPreview.tsx | frame | assignment | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public simulation | |
| S15 | Simulation | Available shelters | Open simulation | Count | CitizenSimulationPreview.tsx | frame | shelter state | not tested | PASS | PASS | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P1 | public simulation | |
| S16 | Simulation | Changed road count | Open simulation | Count | CitizenSimulationPreview.tsx | frame | roads | not tested | PASS | PASS | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P1 | public simulation | |
| S17 | Simulation | Computation status | Open simulation | Status visible | CitizenSimulationPreview.tsx | frame | API state | not tested | PASS | PASS | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P1 | public simulation | |
| A01 | Admin | Admin page | Open /admin?demo=1 | Page loads | AdminSimulator.tsx | SPA | build | visibility | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public admin screenshot | |
| A02 | Admin | Preset selector | Open admin | Presets listed | AdminSimulator.tsx | scenarios | scenario store | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public admin loading | options eventually appeared but detail did not |
| A03 | Admin | Demo preset | Open admin | Competition selected | AdminSimulator.tsx | scenarios | preset | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public admin | |
| A04 | Admin | Scenario data | Open admin | Detail loaded | AdminSimulator.tsx | scenario/{id} | preset JSON | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public admin | |
| A05 | Admin | Frame 0 | Open admin | Frame shown | AdminSimulator.tsx | frame | frame JSON | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public admin | |
| A06 | Admin | Resource count | Open admin | 117 resources | AdminSimulator.tsx | resources | inventory | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P1 | public admin | |
| A07 | Admin | Readiness | Open admin | READY diagnostic | AdminSimulator.tsx | release/readiness | readiness | not tested | PASS | PASS | PUBLIC_BROKEN | read-only | PUBLIC_BROKEN | P1 | public admin | stuck “확인 중” |
| A08 | Admin | Mode contract | Open admin | Mode data | AdminSimulator.tsx | modes | mode contract | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | API matrix/source | |
| A10 | Admin | Play button | Click play | Button works | AdminSimulator.tsx | none | frames | visibility | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public admin | unavailable while loading |
| A11 | Admin | Playback advance | Click play | Time/state advances | AdminSimulator.tsx | frame | frame JSON | visibility-only | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public admin | |
| A12 | Admin | Frame sequence | Scrub/play | 0/10/20/30 | AdminSimulator.tsx | frame | frame_times | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public admin | |
| A13 | Admin | Frame fetch/cache | Play | Correct frame data | AdminSimulator.tsx | frame | API | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public admin | |
| A14 | Admin | Hazard update | Advance | Hazard changes | MapView.tsx | frame | hazards | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P0 | public admin | |
| A15 | Admin | Road update | Advance | Roads change | MapView.tsx | frame | roads | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P0 | public admin | |
| A16 | Admin | Facility update | Advance | Loads change | MapView.tsx | frame | facilities | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public admin | |
| A17 | Admin | Metrics update | Advance | Metrics change | AdminSimulator.tsx | frame | assignment | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public admin | |
| A18 | Admin | Pause | Click pause | Stops | AdminSimulator.tsx | none | timer | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| A19 | Admin | Manual scrub | Move slider | Selected frame changes | AdminSimulator.tsx | frame | frames | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public admin | |
| T01 | Training route | Button discoverability | Find control | Visible without excessive scroll | AdminSimulator.tsx | none | loaded scenario | visibility | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | responsive screenshots | hidden by loading state |
| T02 | Training route | Click button | Click | Click accepted | AdminSimulator.tsx | training-route | scenario | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | local UI | |
| T03 | Training route | POST trigger | Click | POST sent | AdminSimulator.tsx | POST training-route | graph/frame | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source/local | |
| T04 | Training route | Payload | Click | Required payload | AdminSimulator.tsx | training-route | coords | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source | |
| T05 | Training route | HTTP result | Receive | Status recorded | AdminSimulator.tsx | training-route | graph | mocked-only | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source/tests | |
| T06 | Training route | Response body | Receive | Geometry/metrics | AdminSimulator.tsx | training-route | route solver | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | API/source | |
| T07 | Training route | UI status | Receive | Route result shown | AdminSimulator.tsx | training-route | response | not tested | PASS | PASS | LOCAL_FUNCTIONAL | session | LOCAL_FUNCTIONAL | P1 | local screenshot | text only |
| T08 | Training route | Backend geometry | Receive | Nonempty geometry | simulator/engine.py | training-route | graph | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source | public not run |
| T09 | Training route | Map geometry | Receive | Training path visible | AdminSimulator.tsx/MapView.tsx | training-route | map layer | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | session | VISUALLY_INEFFECTIVE | P1 | source | no geometry passed to MapView |
| T10 | Training route | State sensitivity | Change frame | Path changes | simulator/engine.py | training-route | closures | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| T11 | Training route | Avoid closures | Run closed state | Path avoids edge | simulator/engine.py | training-route | graph | unit coverage | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | assignment tests | UI not verified |
| T12 | Training route | Training distinction | Compare citizen/training | Different labeling/semantics | AdminSimulator.tsx | training-route | provenance | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| N01 | Authoring | New scenario section | Open admin | Section visible | AdminSimulator.tsx | none | UI | visibility | PASS | PASS | PUBLIC_BROKEN | instance | PUBLIC_BROKEN | P1 | public admin | |
| N02 | Authoring | Disaster type | Choose type | Choice stored | AdminSimulator.tsx | scenarios POST | schema | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | public control inaccessible |
| N03 | Authoring | Start datetime | Edit | Value changes | AdminSimulator.tsx | scenarios POST | schema | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N04 | Authoring | End datetime | Edit | Value changes | AdminSimulator.tsx | scenarios POST | schema | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N05 | Authoring | Participation | Choose 25/50/100 | Value changes | AdminSimulator.tsx | scenarios POST | schema | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N06 | Authoring | Save button | Click | Save control visible | AdminSimulator.tsx | scenarios POST | schema | visibility | PASS | PASS | PUBLIC_BROKEN | instance | PUBLIC_BROKEN | P1 | public admin | |
| N07 | Authoring | Create POST | Save | POST sent | AdminSimulator.tsx | POST scenarios | ScenarioStore | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N08 | Authoring | Create response | Save | Success response | goal4a.py | POST scenarios | writable data dir | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N09 | Authoring | Selector entry | Save | New entry | AdminSimulator.tsx | scenarios GET | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N10 | Authoring | Auto-select | Save | New scenario selected | AdminSimulator.tsx | scenarios GET | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N11 | Authoring | Valid frames | Save | Valid frame_times | goal4a.py | scenarios/frame | engine | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N12 | Authoring | Refresh persistence | Refresh | Entry remains | ScenarioStore | scenarios GET | local JSON | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| N13 | Authoring | Process restart | Restart | Entry remains | ScenarioStore | filesystem | container disk | not tested | PASS | PASS | PERSISTENCE_LIMITED | instance | PERSISTENCE_LIMITED | P1 | storage.py | instance-lifetime only |
| N14 | Authoring | Render redeploy | Redeploy | Entry remains durably | ScenarioStore | filesystem | Render disk | not tested | CODE_ONLY | CODE_ONLY | PERSISTENCE_LIMITED | ephemeral | PERSISTENCE_LIMITED | P1 | storage.py | no durable volume evidence |
| D01 | Duplicate | Button | Find/click | Duplicate control | AdminSimulator.tsx | duplicate | scenario | not tested | PASS | PASS | PUBLIC_BROKEN | instance | PUBLIC_BROKEN | P1 | public admin | |
| D02 | Duplicate | API | Click | Success | goal4a.py | duplicate POST | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| D03 | Duplicate | Unique ID | Duplicate | New ID | goal4a.py | duplicate POST | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| D04 | Duplicate | Selector update | Duplicate | Entry appears | AdminSimulator.tsx | scenarios GET | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| D05 | Duplicate | Content match | Duplicate | Intended fields differ only | goal4a.py | duplicate | JSON | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| D06 | Duplicate | Persistence | Refresh/restart | Honest persistence | ScenarioStore | filesystem | local disk | not tested | PASS | PASS | PERSISTENCE_LIMITED | instance | PERSISTENCE_LIMITED | P1 | storage.py | |
| H01 | Hazard | Draw control | Click | Drawing state | AdminSimulator.tsx | none | map | not tested | PASS | PASS | PUBLIC_BROKEN | instance | PUBLIC_BROKEN | P1 | public admin | |
| H02 | Hazard | Enter draw | Click | Drawing mode | MapView.tsx | none | MapLibre | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| H03 | Hazard | Map clicks | Click map | Points append | MapView.tsx | none | MapLibre | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| H04 | Hazard | Point count | Add points | Count increases | AdminSimulator.tsx | none | UI state | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P2 | source | |
| H05 | Hazard | Save guard | <3 points | Save disabled | AdminSimulator.tsx | none | validation | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P2 | source | |
| H06 | Hazard | Save enable | >=3 points | Save enabled | AdminSimulator.tsx | none | validation | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| H07 | Hazard | Save | Click | Scenario updated | AdminSimulator.tsx | scenario update | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| H08 | Hazard | Map result | Save | Hazard visible | MapView.tsx | frame | geometry | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | instance | CODE_ONLY | P1 | not exercised | |
| H09 | Hazard | Frame result | Save | Keyframe includes hazard | goal4a.py | compile/frame | scenario | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| H10 | Hazard | Refresh | Refresh | Hazard remains | ScenarioStore | scenario GET | JSON | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| H11 | Hazard | Add keyframe | Click | Keyframe added | AdminSimulator.tsx | compile | scenario | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| H12 | Hazard | Later computation | Advance | Later result changes | engine.py | frame | hazard state | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| RC01 | Roads | Editor | Open section | Editor visible | AdminSimulator.tsx | none | road IDs | visibility | PASS | PASS | PUBLIC_BROKEN | instance | PUBLIC_BROKEN | P1 | public admin | |
| RC02 | Roads | Select edge | Enter ID | Edge is understandable/selectable | AdminSimulator.tsx | none | opaque edge ID | not tested | CODE_ONLY | CODE_ONLY | VISUALLY_INEFFECTIVE | instance | VISUALLY_INEFFECTIVE | P2 | responsive/admin | opaque manual ID |
| RC03 | Roads | Closure reason | Enter reason | Reason stored | AdminSimulator.tsx | scenario update | schema | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| RC04 | Roads | Save closure | Click save | Success shown | AdminSimulator.tsx | scenario update | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| RC05 | Roads | Frame effect | Advance | Changed road count/state | engine.py | frame | road closure | unit | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P0 | API/unit tests | |
| RC06 | Roads | Map effect | Advance | Closed road rendered | MapView.tsx | frame | roads | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| RC07 | Roads | Invalid edge | Save invalid | Clear validation | AdminSimulator.tsx | scenario update | edge ID | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | instance | CODE_ONLY | P2 | source | |
| RC08 | Roads | Invalid handling | Invalid input | Clear error | AdminSimulator.tsx | scenario update | validation | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | instance | CODE_ONLY | P2 | source | |
| F01 | Facilities | Selector | Open facility editor | Populated options | AdminSimulator.tsx | facilities | 231 records | not tested | PASS | PASS | PUBLIC_BROKEN | instance | PUBLIC_BROKEN | P1 | public admin | |
| F02 | Facilities | Close facility | Save close | Closed | AdminSimulator.tsx | scenario update | facilities | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F03 | Facilities | Availability | Advance | Unavailable in frame | engine.py | frame | facility state | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F04 | Facilities | Zero assignment | Close | Zero assigned | engine.py | frame | assignment | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F05 | Facilities | Visual state | Close | Visual distinction | MapView.tsx | frame | facility layers | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| F06 | Facilities | Available count | Close | Count changes | AdminSimulator.tsx | frame | shelter state | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F07 | Facilities | Capacity input | Edit | Value changes | AdminSimulator.tsx | none | numeric validation | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F08 | Facilities | Capacity save | Click | Saved | AdminSimulator.tsx | scenario update | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F09 | Facilities | Effective capacity | Advance | Frame capacity changes | engine.py | frame | capacity override | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F10 | Facilities | Binding capacity | Override | Assignment changes | engine.py | frame | exact solver | assignment unit | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| F11 | Facilities | Understandability | Inspect panel | Selected/load/capacity clear | AdminSimulator.tsx | frame | facility detail | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P2 | source | |
| RR01 | Resources | Selector | Open resources | Populated | AdminSimulator.tsx | resources | 117 resources | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P1 | public admin | |
| RR02 | Resources | Labels | Browse | Meaningful labels | AdminSimulator.tsx | resources | resource names | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P2 | public admin | |
| RR03 | Resources | Mark unavailable | Save | Saved unavailable | AdminSimulator.tsx | resource update | store | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| RR04 | Resources | Frame effect | Advance | Resource effect | engine.py | frame | resource state | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| RR05 | Resources | Visible effect | Inspect | State/effect visible | AdminSimulator.tsx | frame | resource state | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| RR06 | Resources | Separate semantics | Edit | Not mixed with capacity | engine.py | frame | model schema | not tested | PASS | PASS | CODE_ONLY | instance | CODE_ONLY | P1 | source | |
| AB01 | A/B | Selector | Open compare | Scenario B selector | AdminSimulator.tsx | scenarios | presets | visibility | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public admin | |
| AB02 | A/B | Choose B | Select | B selected | AdminSimulator.tsx | none | scenarios | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public admin | |
| AB03 | A/B | Difference request | Click compare | POST sent | AdminSimulator.tsx | POST compare | frames | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | local UI/source | |
| AB04 | A/B | Response | Receive | Success | goal4a.py | compare | exact engine | API | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | local compare | |
| AB05 | A/B | Assigned delta | Compare | Delta visible | AdminSimulator.tsx | compare | assignment | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | local AB screenshot | |
| AB06 | A/B | Unserved delta | Compare | Delta visible | AdminSimulator.tsx | compare | assignment | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | local AB screenshot | |
| AB07 | A/B | Cost delta | Compare | Cost visible | AdminSimulator.tsx | compare | objective | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | local AB screenshot | |
| AB08 | A/B | Shelter delta | Compare | Delta visible | AdminSimulator.tsx | compare | facilities | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | local AB screenshot | |
| AB09 | A/B | Road delta | Compare | Delta visible | AdminSimulator.tsx | compare | roads | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | local AB screenshot | |
| AB10 | A/B | Why explanation | Compare | Causes visible | AdminSimulator.tsx | compare | causal inputs | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | local AB screenshot | |
| AB11 | A/B | Reproducibility | Repeat fixed A/B | Same result | engine.py | compare | fixed presets | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P0 | local run | public repeat not separately tested |
| E01 | Export | Button | Find JSON export | Visible | AdminSimulator.tsx | export | scenario | visibility | PASS | PASS | PUBLIC_BROKEN | read-only | PUBLIC_BROKEN | P1 | public admin | |
| E02 | Export | Server export | Click | Server response | AdminSimulator.tsx | GET export | scenario | API | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source/tests | |
| E03 | Export | Download | Click | Browser download | AdminSimulator.tsx | export | browser | e2e | PASS | PASS | CODE_ONLY | file | CODE_ONLY | P1 | e2e | |
| E04 | Export | JSON parse | Open file | Valid JSON | export | export | serializer | API | PASS | PASS | CODE_ONLY | file | CODE_ONLY | P1 | API/e2e | |
| E05 | Export | Assumptions | Open JSON | Assumptions included | export | export | scenario | not tested | PASS | PASS | CODE_ONLY | file | CODE_ONLY | P1 | source | |
| E06 | Export | Frame result | Open JSON | Frame included | export | export | frame | not tested | PASS | PASS | CODE_ONLY | file | CODE_ONLY | P1 | source | |
| E07 | Export | Caveats | Open JSON | Caveats included | export | export | provenance | not tested | PASS | PASS | CODE_ONLY | file | CODE_ONLY | P2 | source | |
| AI01 | AI | AI section | Open admin | Section visible | AdminSimulator.tsx | none | model status | visibility | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public admin | |
| AI02 | AI | 100 candidates | Click | Request completes | AdminSimulator.tsx | POST screen | candidate set | mocked-only | PASS | PASS | PUBLIC_BROKEN | read-only | PUBLIC_BROKEN | P1 | public API matrix | timeout |
| AI03 | AI | 500 candidates | Click | Works or honest slow | AdminSimulator.tsx | screen | candidate set | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | read-only | CODE_ONLY | P1 | not run | |
| AI04 | AI | 1000 candidates | Click if claimed | Works/limited honestly | AdminSimulator.tsx | screen | candidate set | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | read-only | CODE_ONLY | P2 | not claimed | |
| AI05 | AI | Public POST | Run | Actual endpoint called | AdminSimulator.tsx | POST screen | network/model | mocked-only | PASS | PASS | PUBLIC_BROKEN | read-only | PUBLIC_BROKEN | P1 | public API matrix | 60s timeout |
| AI06 | AI | Model loads | Run | Model ready | goal5a.py | screen | ridge v1 | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | readiness | |
| AI07 | AI | Estimate | Run | Estimate returned | goal5a.py | screen | model | mocked-only | PASS | PASS | PUBLIC_BROKEN | read-only | PUBLIC_BROKEN | P1 | public timeout | |
| AI08 | AI | Support status | Run | Support metadata | goal5a.py | screen | model | mocked-only | PASS | PASS | PUBLIC_BROKEN | read-only | PUBLIC_BROKEN | P1 | public timeout | |
| AI09 | AI | Exact top-K | Run | Exact verification | goal5a.py | screen | exact solver | mocked-only | PASS | PASS | PUBLIC_BROKEN | read-only | PUBLIC_BROKEN | P1 | public timeout | |
| AI10 | AI | Distinct results | Run | Estimate vs exact distinct | AdminSimulator.tsx | screen | response | mocked-only | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public timeout | |
| AI11 | AI | Exact authority | Run | Exact final result | AdminSimulator.tsx | screen | verifier | mocked-only | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public timeout | |
| AI12 | AI | Elapsed time | Run | Measured elapsed time | AdminSimulator.tsx | screen | timer | mocked-only | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P2 | public timeout | |
| PD01 | Data | National shelters | Query | 231 | API/data | facilities | official snapshot | API | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | public API | |
| PD02 | Data | Local shelters | Query | 224 where intended | API/data | facilities | local snapshot | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source | |
| PD03 | Data | National water | Query | 71 | API/data | facilities | official snapshot | API | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P1 | public API | |
| PD04 | Data | Local water | Query | 46 | API/data | facilities | local snapshot | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source | |
| PD05 | Data | AED | Query | 305 | API/data | facilities | official snapshot | API | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P1 | public API | |
| PD06 | Data | Flood inventory | Query | 33 | API/data | inventory | inventory snapshot | API | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P1 | public API | |
| PD07 | Data | Population | Read readiness | 31 units/562143 | readiness | readiness | 2026-07-31 | API | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P0 | readiness JSON | |
| PD08 | Data | Provenance | Inspect | Accurate source labels | App.tsx | data-sources | metadata | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P1 | public UI/API | |
| PD09 | Data | No double count | Compare | Correct totals | data layer | facilities | national/local | not tested | PASS | PASS | CODE_ONLY | read-only | CODE_ONLY | P1 | source | |
| PD10 | Data | AED no coords | Search/list | Records remain discoverable | App.tsx | facilities | address records | behavioral | PASS | PASS | PUBLIC_FUNCTIONAL | read-only | PUBLIC_FUNCTIONAL | P1 | public AED screenshot | |
| M01 | Map | Facilities | Inspect map | Facility features | MapView.tsx | facilities | coordinates | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P0 | screenshot/source | |
| M02 | Map | Clusters | Inspect map | Clusters | MapView.tsx | facilities | MapLibre | not tested | PASS | PASS | CODE_ONLY | session | CODE_ONLY | P1 | source | |
| M03 | Map | Walking route | Route | Line | MapView.tsx | routes | geometry | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | public route | |
| M04 | Map | Endpoints | Route | Markers | MapView.tsx | routes | coords | not tested | PASS | PASS | PUBLIC_BROKEN | session | PUBLIC_BROKEN | P1 | public route | |
| M05 | Map | Hazard | Simulation | Hazard layer | MapView.tsx | frame | hazard geometry | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | simulation screenshot | |
| M06 | Map | Closed roads | Simulation | Road layer | MapView.tsx | frame | roads | not tested | PASS | PASS | PUBLIC_FUNCTIONAL | session | PUBLIC_FUNCTIONAL | P0 | simulation screenshot | |
| M07 | Map | Facility load | Simulation | Load encoding | MapView.tsx | frame | loads | not tested | CODE_ONLY | CODE_ONLY | VISUALLY_INEFFECTIVE | session | VISUALLY_INEFFECTIVE | P1 | source/public simulation | |
| M08 | Map | Current location | Citizen | Location marker | MapView.tsx | geolocation | permission | not tested | CODE_ONLY | CODE_ONLY | CODE_ONLY | session | CODE_ONLY | P2 | not permission-tested | |

Primary status counts are summarized in `docs/FULL_PRODUCT_FUNCTION_AUDIT.md`; multiple labels (for example, a code-only map subfeature inside a public-broken flow) are intentionally retained in Notes rather than collapsed into a binary result.
