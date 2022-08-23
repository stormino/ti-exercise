# ThinkIN exercies

## Overall architecture

```mermaid
flowchart LR;
    consumer-->|message| ingestion1
    consumer-->|message| ingestion2
    consumer-->|message| ingestion3
    p1-->|http| consumer
    p2-->|http| consumer
    p3-->|http| consumer
    ingestion1-->|message| postprocessing
    ingestion2-->|message| postprocessing
    ingestion3-->|message| postprocessing
    subgraph Pusher
        p1
        p2
        p3
    end
    subgraph Extractor
        subgraph e1
            ingestion1
        end
        subgraph e2
            ingestion2
        end
        subgraph e3
            ingestion3
        end
        postprocessing
    end
```

1. The consumer component will receive via HTTP batches of sensor data;
2. The consumer component will produce messages for each received batch of data;
3. Messages will be consumed by extractor component instance(s) - service is designed to be scalable;
4. Extractor will handle batches and extract increasing sequences of sensor values;
5. Extractor will also take care of writing the longest sequence ever seen into a file (for each instance).

## How to use the solution

### Requirements

Docker / docker compose are required to take advantage of the already prepared dev and production environment (`docker-compose.yml` and `docker-compose.dev.yml`).

### Run the solution

To run the solution without the hassle of configuration and compiling, just run the following command:  
`docker-compose -p ti-exercise up -d`

> Please note that by default extractor scales to 3 instances.

After that, you can run one or more python pushers against the exposed consumer endpoint reachable at `localhost:18888` using the following command:  
`python pusher.py http://localhost:18888/sensor <fromId> <toId> <sleep>`  
It may be necessary to download python packages such as `requests`:  
`pip install requests`

To query the extractor service looking for saved sequences overlapping a certain period, you can run the following command:  
```
curl -L -X POST 'http://localhost/sequence' \
-H 'Host: extractor.docker.localhost' \
-H 'Content-Type: application/json' \
--data-raw '{
	"sensorId": 1,
    "dateFrom": 1661278877026,
    "dateTo": 1661278881079
}'
```

> Please note that you have to specify the customized `Host` header

To retrieve the content of the `longestsequence.log` file, run the following command:  
`docker exec -it ti-exercise_extractor_1 cat longestsequence.log`

> You can execute the command against another instance of the extractor service, but the file content should be the same ;)

To check against MongoDB if the sequence is indeed the longest ever seen, follow the steps:
1. Open a bash for the mongo container:  
`docker exec -it mongo /bin/bash`
2. Connect to mongo instance using the brand new fashionable client:  
`mongosh mongodb://root_user:mongo_r00t_pw\!@localhost:27017`
3. Connect to the application database:  
`use ti-exercise`
4. Execute the following aggregation query:  
    ```
    db.sequence.aggregate([
        { $addFields: { valuesSize: { $size: "$values" } } },
        { $sort: { valuesSize: -1 } },
        { $limit: 1 }
    ])
    ```
5. The sequence should be the same as the one observed in the file.

### Observations and hints
To provide access to extractor service instances via HTTP, a reverse proxy (Traefik) has been configured for this service.  
To access the traefik dashboard, just connect to http://localhost:8888/  
No attention has been paid whatsoever to security aspects such as unencrypted passwords, plain text communications and so on. To me, it would have been overkilling for the purpose of the exercise.  
To leverage git capabilities without losing (micro)services independence and self-containment (codebase, deploy, CI/CD, etc.), I've made the choice to set up a main repo for the environment and provided utilities referring each service repo using git submodules.