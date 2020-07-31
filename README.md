# SocialKB
SocialKB is a system for modeling Twitter data and reasoning about the data for discovering malicious content and suspicious users.

SocialKB uses Markov logic networks (MLNs) for modeling and inference. It uses Tuffy as the MLN engine. Tuffy has been obtained from http://i.stanford.edu/hazy/tuffy/. Please visit this page to download Tuffy.

## Setup
1. System Setup.
    ```
    cd scripts && source setup.sh
    ```
   
2. Collect Twitter Data and Construct Evidence
    1. Update twitter keys along with the number of tweets to be collected at `scripts/construct-evidence.sh`
    2. Construct evidence db
        ```
        bash construct-evidence.sh
        ```
 
3. Setup Tuffy
    1. Setup PostgreSQL 
        ```
        cd scripts && bash postgresql_setup.sh
        ```
    2. Update `tuffy.conf` with the username

4. Weight Learning
    ```
    java -jar tuffy.jar -learnwt -e <EVIDENCE_DIR>/evidence.db -i input/prog.mln -queryFile input/query.db -r lrnt.prog.mln -mcsatSamples 50 -dMaxIter 100
    ```
5. Inference
    1. MAP Inference:
        ```
        java -jar tuffy.jar -e <EVIDENCE_DIR>/evidence.db -i input/lrnt.prog.mln  -queryFile input/query.db -r out.txt
        ```
    2. Marginal Inference:
        ```
        java -jar tuffy.jar  -marginal -e <EVIDENCE_DIR>/evidence.db -i input/lrnt.prog.mln  -queryFile input/query.db -r out.txt
        ```
       
## Publications

* Praveen Rao, Anas Katib, Charles Kamhoua, Kevin Kwiat, and Laurent Njilla. "Probabilistic Inference on Twitter Data to Discover Suspicious Users and Malicious Content." In the 2nd IEEE International Symposium on Security and Privacy in Social Networks and Big Data (SocialSec 2016), pages 407-414, Nadi, Fiji, December 2016. [PDF](http://r.web.umkc.edu/raopr/SocialKB-SocialSec-2016.pdf)

* Praveen Rao, Charles Kamhoua, Laurent Njilla, Kevin Kwiat. "Methods to Detect Cyberthreats on Twitter." In Surveillance in Action - Technologies for Civilian, Military and Cyber Surveillance, pages 333-350, Springer, 2017.

## Patents

* Praveen Rao, Charles Kamhoua, Kevin Kwiat, Laurent Njilla. "System and Article of Manufacture to Analyze Twitter Data to Discover Suspicious Users and Malicious Content," US Patent, Sr. No. 10,348,752, July 9, 2019.

## Contributors

***Faculty:*** Praveen Rao (PI)

***PhD Students:*** Anas Katib, Arun Zachariah

***Others:*** Charles Kamhoua, Kevin Kwiat, and Laurent Njilla

## Acknowledgments
The first author (P.R.) was supported by the U.S. Air Force Summer Faculty Fellowship and the National Research Council Research Associateship Senior Fellowship Award.
