/* Copyright (C) 2023-2024, RV Bionics Group SpA.
 * Copyright (C) 2009 Trend Micro Inc.
 * All right reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 3) as published by the FSF - Free Software
 * Foundation
 */

#include "shared.h"
#include "rules.h"
#include "cdb/cdb.h"
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

ListNode *os_analysisd_cdblists;
ListRule *os_analysisd_cdbrules;

/* Create the ListRule */
void OS_CreateListsList() {
    os_analysisd_cdblists = NULL;
    os_analysisd_cdbrules = NULL;
}

void OS_ListLoadRules(ListNode **l_node, ListRule **lrule) {

    while (*lrule != NULL) {

        if (!(*lrule)->loaded) {
            (*lrule)->db = OS_FindList((*lrule)->filename, l_node);
            (*lrule)->loaded = 1;
        }

        *lrule = (*lrule)->next;
    }
}

/* External AddList */
void OS_AddList(ListNode *new_listnode, ListNode **cdblists) {

    if (*cdblists == NULL) {
        /* First list */
        *cdblists = new_listnode;
    } else {
        /* Add new list to the end */
        ListNode *last_list_node = *cdblists;

        while (last_list_node->next != NULL) {
            last_list_node = last_list_node->next;
        }
        last_list_node->next = new_listnode;

    }
}

ListNode *OS_FindList(const char *listname, ListNode **l_node) {

    ListNode *last_list_node = *l_node;
    if (last_list_node != NULL) {
        do {
            if (strcmp(last_list_node->txt_filename, listname) == 0 ||
                    strcmp(last_list_node->cdb_filename, listname) == 0) {
                /* Found first match returning */
                return (last_list_node);
            }
            last_list_node = last_list_node->next;
        } while (last_list_node != NULL);
    }
    return (NULL);
}

ListRule *OS_AddListRule(ListRule *first_rule_list, int lookup_type, int field,
                         const char *dfield, char *listname, OSMatch *matcher,
                         ListNode **l_node) {

    ListRule *new_rulelist_pt = NULL;
    new_rulelist_pt = (ListRule *)calloc(1, sizeof(ListRule));
    if (!new_rulelist_pt) {
        return (NULL);
    }

    new_rulelist_pt->field = field;
    new_rulelist_pt->next = NULL;
    new_rulelist_pt->matcher = matcher;
    new_rulelist_pt->lookup_type = lookup_type;
    new_rulelist_pt->filename = strdup(listname);
    new_rulelist_pt->dfield = field == RULE_DYNAMIC ? strdup(dfield) : NULL;
    new_rulelist_pt->mutex = (pthread_mutex_t) PTHREAD_MUTEX_INITIALIZER;

    if ((new_rulelist_pt->db = OS_FindList(listname, l_node)) == NULL) {
        os_free(new_rulelist_pt->filename);
        os_free(new_rulelist_pt->dfield);
        os_free(new_rulelist_pt);
        return NULL;
    }
    
    new_rulelist_pt->loaded = 1;

    if (first_rule_list == NULL) {
        mdebug1("Adding First rulelist item: filename: %s field: %d lookup_type: %d",
               new_rulelist_pt->filename,
               new_rulelist_pt->field,
               new_rulelist_pt->lookup_type);
        first_rule_list = new_rulelist_pt;
    } else {
        while (first_rule_list->next) {
            first_rule_list = first_rule_list->next;
        }
        mdebug1("Adding rulelist item: filename: %s field: %d lookup_type: %d",
               new_rulelist_pt->filename,
               new_rulelist_pt->field,
               new_rulelist_pt->lookup_type);
        first_rule_list->next = new_rulelist_pt;
    }
    return first_rule_list;
}

static int _OS_CDBOpen(ListNode *lnode)
{
    int fd;
    if (lnode->loaded != 1) {
        if ((fd = open(lnode->cdb_filename, O_RDONLY)) == -1) {
            merror(OPEN_ERROR, lnode->cdb_filename, errno, strerror (errno));
            return -1;
        }
        cdb_init(&lnode->cdb, fd);
        lnode->loaded = 1;
    }
    return 0;
}

static int OS_DBSearchKeyValue(ListRule *lrule, char *key)
{
    int result = -1;
    char *val;
    unsigned vlen, vpos;
    w_mutex_lock(&lrule->mutex);
    if (lrule->db != NULL) {
        if (_OS_CDBOpen(lrule->db) == -1) {
            w_mutex_unlock(&lrule->mutex);
            return 0;
        }
        if (cdb_find(&lrule->db->cdb, key, strlen(key)) > 0 ) {
            vpos = cdb_datapos(&lrule->db->cdb);
            vlen = cdb_datalen(&lrule->db->cdb);
            val = (char *) calloc(vlen + 1, sizeof(char));

            w_mutex_unlock(&lrule->mutex);
            if (!val){
                return 0;
            }

            w_mutex_lock(&lrule->db->cdb.mutex)
            cdb_read(&lrule->db->cdb, val, vlen, vpos);
            w_mutex_unlock(&lrule->db->cdb.mutex);
            result = OSMatch_Execute(val, vlen, lrule->matcher);
            free(val);
            return result;
        } else {
            w_mutex_unlock(&lrule->mutex);
            return 0;
        }
    }
    w_mutex_unlock(&lrule->mutex);
    return 0;
}

static int OS_DBSeachKey(ListRule *lrule, char *key)
{
    w_mutex_lock(&lrule->mutex);
    if (lrule->db != NULL) {
        if (_OS_CDBOpen(lrule->db) == -1) {
            w_mutex_unlock(&lrule->mutex);
            return -1;
        }
        w_mutex_unlock(&lrule->mutex);
        if ( cdb_find(&lrule->db->cdb, key, strlen(key)) > 0 ) {
            return 1;
        }
    }else {
        w_mutex_unlock(&lrule->mutex);
    }
    return 0;
}

static int OS_DBSeachKeyAddress(ListRule *lrule, char *key)
{
    w_mutex_lock(&lrule->mutex);
    if (lrule->db != NULL) {
        if (_OS_CDBOpen(lrule->db) == -1) {
            w_mutex_unlock(&lrule->mutex);
            return -1;
        }
        w_mutex_unlock(&lrule->mutex);
        if ( cdb_find(&lrule->db->cdb, key, strlen(key)) > 0 ) {
            return 1;
        } else {
            char *tmpkey;
            os_strdup(key, tmpkey);
            while (strlen(tmpkey) > 0) {
                if (tmpkey[strlen(tmpkey) - 1] == '.') {
                    if ( cdb_find(&lrule->db->cdb, tmpkey, strlen(tmpkey)) > 0 ) {
                        free(tmpkey);
                        return 1;
                    }
                }
                tmpkey[strlen(tmpkey) - 1] = '\0';
            }
            free(tmpkey);
        }
    }else{
        w_mutex_unlock(&lrule->mutex);
    }
    return 0;
}

static int OS_DBSearchKeyAddressValue(ListRule *lrule, char *key)
{
    int result = -1;
    char *val;
    unsigned vlen, vpos;
    w_mutex_lock(&lrule->mutex);
    if (lrule->db != NULL) {
        if (_OS_CDBOpen(lrule->db) == -1) {
            w_mutex_unlock(&lrule->mutex);
            return 0;
        }

        w_mutex_unlock(&lrule->mutex);

        /* First lookup for a single IP address */
        if (cdb_find(&lrule->db->cdb, key, strlen(key)) > 0 ) {
            vpos = cdb_datapos(&lrule->db->cdb);
            vlen = cdb_datalen(&lrule->db->cdb);
            os_calloc(vlen, sizeof(char), val);
            w_mutex_lock(&lrule->db->cdb.mutex)
            cdb_read(&lrule->db->cdb, val, vlen, vpos);
            w_mutex_unlock(&lrule->db->cdb.mutex)
            result = OSMatch_Execute(val, vlen, lrule->matcher);
            free(val);
            return result;
        } else {
            /* IP address not found, look for matching subnets */
            char *tmpkey;
            os_strdup(key, tmpkey);
            while (strlen(tmpkey) > 0) {
                if (tmpkey[strlen(tmpkey) - 1] == '.') {
                    if ( cdb_find(&lrule->db->cdb, tmpkey, strlen(tmpkey)) > 0 ) {
                        vpos = cdb_datapos(&lrule->db->cdb);
                        vlen = cdb_datalen(&lrule->db->cdb);
                        os_calloc(vlen, sizeof(char), val);
                        w_mutex_lock(&lrule->db->cdb.mutex)
                        cdb_read(&lrule->db->cdb, val, vlen, vpos);
                        w_mutex_unlock(&lrule->db->cdb.mutex)
                        result = OSMatch_Execute(val, vlen, lrule->matcher);
                        free(val);
                        free(tmpkey);
                        return result;
                    }
                }
                tmpkey[strlen(tmpkey) - 1] = '\0';
            }
            free(tmpkey);
            return 0;
        }
    }else{
        w_mutex_unlock(&lrule->mutex);
    }
    return 0;
}

int OS_DBSearch(ListRule *lrule, char *key, ListNode **l_node)
{
    //XXX - god damn hack!!! Jeremy Rossi
    w_mutex_lock(&lrule->mutex);
    if (lrule->loaded == 0) {
        lrule->db = OS_FindList(lrule->filename, l_node);
        lrule->loaded = 1;
    }
    w_mutex_unlock(&lrule->mutex);

    switch (lrule->lookup_type) {
        case LR_STRING_MATCH:
            if (OS_DBSeachKey(lrule, key) == 1) {
                return 1;
            }
            return 0;
        case LR_STRING_NOT_MATCH:
            if (OS_DBSeachKey(lrule, key) == 1) {
                return 0;
            }
            return 1;
        case LR_STRING_MATCH_VALUE:
            if (OS_DBSearchKeyValue(lrule, key) == 1) {
                return 1;
            }
            return 0;
        case LR_ADDRESS_MATCH:
            return OS_DBSeachKeyAddress(lrule, key) == 1;
        case LR_ADDRESS_NOT_MATCH:
            if (OS_DBSeachKeyAddress(lrule, key) == 0) {
                return 1;
            }
            return 0;
        case LR_ADDRESS_MATCH_VALUE:
            if (OS_DBSearchKeyAddressValue(lrule, key) == 0) {
                return 1;
            }
            return 0;
        default:
            mdebug1("lists_list.c::OS_DBSearch should never hit default");
            return 0;
    }
}

void os_remove_cdblist(ListNode **l_node) {

    ListNode *tmp;

    while (*l_node) {

        tmp = *l_node;
        *l_node = (*l_node)->next;

        os_free(tmp->cdb_filename);
        os_free(tmp->txt_filename);
        os_free(tmp);
    }

}

void os_remove_cdbrules(ListRule **l_rule) {

    ListRule *tmp;

    while (*l_rule) {

        tmp = *l_rule;
        *l_rule = (*l_rule)->next;

        if (tmp->matcher) OSMatch_FreePattern(tmp->matcher);
        os_free(tmp->matcher);
        os_free(tmp->dfield);
        os_free(tmp->filename);
        os_free(tmp);
    }

}
