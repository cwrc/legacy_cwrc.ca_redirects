# CWRC Redirect Rewrite Map File

Redirected URL paths based on Drupal 7 / Islandora URL paths.

## Overview

The original instance of the CWRC Repository was hosted on Islandora / Drupal 7 and during the migration to Drupal 10 / Islandora 2, the URL path changed. To retain the availability of the old url path to prevent dead links, a redirect mapping that translates an old URL path to the new URL path. This also allows a staged migration from legacy Drupal 7 to the new LEAF/Islandroa based Drupal 10+ instance where URL paths of not yet migrated content redirect to a legacy instance while migrated content redirect to the new isntance.

Technologies considered
* Redirect at the ingress controller: this would allow only redirect for the not yet migrated content however the current version does not handle the scale of not yet migrated content (unlike the previous version). As the list decreases to a small 5 figure number then this might be viable.
* Drupal: decided against to reduce DB load
* Apache redirect rewrite map file: the approach works without adding DB load but requires more time to update

## Update the Apache Rewrite Map file 

```
# Generate the updated Drupal DB dump of the path_alias table 
drush sqlq "SELECT path, alias FROM path_alias;" > /var/www/drupal/private/v2.cwrc.ca_path_alias_$(date +"%Y-%m-%d_%H-%M-%S").txt

Get current [./map_file/rewrite_map_cwrc.ca_islandora_object_pid.txt] file

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
python3 update_rewrite_mapping.py \
  --input_drupal ./tmp/v2.cwrc.ca_path_alias_2025-08-21.txt \
  --input_rewrite_map ./map_file/rewrite_map_cwrc.ca_islandora_object_pid.txt \
  --output ./tmp/rewrite_map_cwrc.ca_islandora_object_pid.${TIMESTAMP}.txt 

# check for expected updates in the redirect target path
diff \
  ./map_file/rewrite_map_cwrc.ca_islandora_object_pid.txt \
  ./tmp/rewrite_map_cwrc.ca_islandora_object_pid.${TIMESTAMP}.txt

# update version stored in Git repository
mv ./tmp/rewrite_map_cwrc.ca_islandora_object_pid.${TIMESTAMP}.txt ./map_file/rewrite_map_cwrc.ca_islandora_object_pid.txt 

git commit

# Regenerate rewrite mapping file
httxt2dbm -f SDBM \
  -i ./map_file/rewrite_map_cwrc.ca_islandora_object_pid.txt \
  -o ./tmp/rewrite_map_cwrc.ca_islandora_object_pid

# Copy resulting rewrite_map_cwrc.ca_islandora_object_pid.dir and rewrite_map_cwrc.ca_islandora_object_pid.pg to the cwrc_static container volume.

# Restart cwrc_static container
```

## Testing

* Display the lines that contain a given ID based on a file containing a list of IDs 
    ```
    while read -r line; do grep ${line} a; done < "/tmp/z"
    ```
