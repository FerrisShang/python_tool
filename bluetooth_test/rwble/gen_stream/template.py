from rw_code2stream import *
from collections import OrderedDict
c = OrderedDict()

c['L2CC_CMP_EVT'] = '''
        puts("00");
    '''
c['L2CC_LECB_CONNECT_CMD'] = '''
        puts("00");
    '''
c['L2CC_LECB_CONNECT_REQ_IND'] = '''
        puts("00");
    '''
c['L2CC_LECB_CONNECT_CFM'] = '''
        puts("00");
    '''
c['L2CC_LECB_CONNECT_IND'] = '''
        puts("00");
    '''
c['L2CC_LECB_DISCONNECT_CMD'] = '''
        puts("00");
    '''
c['L2CC_LECB_DISCONNECT_IND'] = '''
        puts("00");
    '''
c['L2CC_LECB_ADD_CMD'] = '''
        puts("00");
    '''
c['L2CC_LECB_ADD_IND'] = '''
        puts("00");
    '''
c['L2CC_LECB_SDU_SEND_CMD'] = '''
        puts("00");
    '''
c['L2CC_LECB_SDU_RECV_IND'] = '''
        puts("00");
    '''
c['L2CC_UNKNOWN_MSG_IND'] = '''
        puts("00");
    '''
c['L2CC_DBG_PDU_SEND_CMD'] = '''
        puts("00");
    '''
c['L2CC_DBG_PDU_RECV_IND'] = '''
        puts("00");
    '''
c['L2CC_PDU_SEND_CMD'] = '''
        puts("00");
    '''
c['L2CC_PDU_RECV_IND'] = '''
        puts("00");
    '''
c['L2CC_SIGNALING_TRANS_TO_IND'] = '''
        puts("00");
    '''
c['GATTM_ADD_SVC_REQ'] = '''
        puts("00");
    '''
c['GATTM_ADD_SVC_RSP'] = '''
        puts("00");
    '''
c['GATTM_SVC_GET_PERMISSION_REQ'] = '''
        puts("00");
    '''
c['GATTM_SVC_GET_PERMISSION_RSP'] = '''
        puts("00");
    '''
c['GATTM_SVC_SET_PERMISSION_REQ'] = '''
        puts("00");
    '''
c['GATTM_SVC_SET_PERMISSION_RSP'] = '''
        puts("00");
    '''
c['GATTM_ATT_GET_PERMISSION_REQ'] = '''
        puts("00");
    '''
c['GATTM_ATT_GET_PERMISSION_RSP'] = '''
        puts("00");
    '''
c['GATTM_ATT_SET_PERMISSION_REQ'] = '''
        puts("00");
    '''
c['GATTM_ATT_SET_PERMISSION_RSP'] = '''
        puts("00");
    '''
c['GATTM_ATT_GET_VALUE_REQ'] = '''
        puts("00");
    '''
c['GATTM_ATT_GET_VALUE_RSP'] = '''
        puts("00");
    '''
c['GATTM_ATT_SET_VALUE_REQ'] = '''
        puts("00");
    '''
c['GATTM_ATT_SET_VALUE_RSP'] = '''
        puts("00");
    '''
c['GATTM_DESTROY_DB_REQ'] = '''
        puts("00");
    '''
c['GATTM_DESTROY_DB_RSP'] = '''
        puts("00");
    '''
c['GATTM_SVC_GET_LIST_REQ'] = '''
        puts("00");
    '''
c['GATTM_SVC_GET_LIST_RSP'] = '''
        puts("00");
    '''
c['GATTM_ATT_GET_INFO_REQ'] = '''
        puts("00");
    '''
c['GATTM_ATT_GET_INFO_RSP'] = '''
        puts("00");
    '''
c['GATTC_CMP_EVT'] = '''
        puts("00");
    '''
c['GATTC_EXC_MTU_CMD'] = '''
        puts("00");
    '''
c['GATTC_MTU_CHANGED_IND'] = '''
        puts("00");
    '''
c['GATTC_DISC_CMD'] = '''
        puts("00");
    '''
c['GATTC_DISC_SVC_IND'] = '''
        puts("00");
    '''
c['GATTC_DISC_SVC_INCL_IND'] = '''
        puts("00");
    '''
c['GATTC_DISC_CHAR_IND'] = '''
        puts("00");
    '''
c['GATTC_DISC_CHAR_DESC_IND'] = '''
        puts("00");
    '''
c['GATTC_READ_CMD'] = '''
        puts("00");
    '''
c['GATTC_READ_IND'] = '''
        puts("00");
    '''
c['GATTC_WRITE_CMD'] = '''
        puts("00");
    '''
c['GATTC_EXECUTE_WRITE_CMD'] = '''
        puts("00");
    '''
c['GATTC_EVENT_IND'] = '''
        puts("00");
    '''
c['GATTC_EVENT_REQ_IND'] = '''
        puts("00");
    '''
c['GATTC_EVENT_CFM'] = '''
        puts("00");
    '''
c['GATTC_REG_TO_PEER_EVT_CMD'] = '''
        puts("00");
    '''
c['GATTC_SEND_EVT_CMD'] = '''
        puts("00");
    '''
c['GATTC_SEND_SVC_CHANGED_CMD'] = '''
        puts("00");
    '''
c['GATTC_SVC_CHANGED_CFG_IND'] = '''
        puts("00");
    '''
c['GATTC_READ_REQ_IND'] = '''
        puts("00");
    '''
c['GATTC_READ_CFM'] = '''
        puts("00");
    '''
c['GATTC_WRITE_REQ_IND'] = '''
        puts("00");
    '''
c['GATTC_WRITE_CFM'] = '''
        puts("00");
    '''
c['GATTC_ATT_INFO_REQ_IND'] = '''
        puts("00");
    '''
c['GATTC_ATT_INFO_CFM'] = '''
        puts("00");
    '''
c['GATTC_SDP_SVC_DISC_CMD'] = '''
        puts("00");
    '''
c['GATTC_SDP_SVC_IND'] = '''
        puts("00");
    '''
c['GATTC_TRANSACTION_TO_ERROR_IND'] = '''
        puts("00");
    '''
c['GATTC_UNKNOWN_MSG_IND'] = '''
        puts("00");
    '''
c['GAPM_CMP_EVT'] = '''
        struct gapm_cmp_evt *m = KE_MSG_ALLOC(GAPM_CMP_EVT, TASK_GAPM, TASK_AHI, gapm_cmp_evt);
        m->operation = GAPM_RESET;
        m->status = GAP_ERR_NO_ERROR;
        dump(m);
    '''
c['GAPM_RESET_CMD'] = '''
        struct gapm_reset_cmd *m = KE_MSG_ALLOC(GAPM_RESET_CMD, TASK_GAPM, TASK_AHI, gapm_reset_cmd);
        m->operation = GAPM_RESET;
        dump(m);
    '''
c['GAPM_SET_DEV_CONFIG_CMD'] = '''
        struct gapm_set_dev_config_cmd gapm_set_dev_config_cmd = {
            .operation = GAPM_SET_DEV_CONFIG,
            .role = GAP_ROLE_ALL,
            .renew_dur = RPA_TO_DFT,
            .addr = {{0x5F,0x5F,0x5F,0x5F,0x5F,0x5F}},
            .irk = {{0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01}},
            .privacy_cfg = GAPM_PRIV_CFG_PRIV_EN_BIT, //public addr & privacy enabled
            .pairing_mode = GAPM_PAIRING_LEGACY,
            .gap_start_hdl = 0,
            .gatt_start_hdl = 0,
            .att_cfg = 0,
            .sugg_max_tx_octets = BLE_MAX_OCTETS,
            .sugg_max_tx_time = BLE_MAX_TIME,
            .max_mtu = 23,
            .max_mps = 23,
            .max_nb_lecb = 0,
            .audio_cfg = 0,
            .tx_pref_phy = GAP_PHY_ANY,
            .rx_pref_phy = GAP_PHY_ANY,
            .tx_path_comp = 0,
            .rx_path_comp = 0,
        };

        struct gapm_set_dev_config_cmd *m = KE_MSG_ALLOC(GAPM_SET_DEV_CONFIG_CMD, TASK_GAPM, TASK_AHI, gapm_set_dev_config_cmd);
        memcpy(m, &gapm_set_dev_config_cmd, sizeof(struct gapm_set_dev_config_cmd));
        dump(m);
    '''
c['GAPM_SET_CHANNEL_MAP_CMD'] = '''
        puts("00");
    '''
c['GAPM_GET_DEV_INFO_CMD'] = '''
        puts("00");
    '''
c['GAPM_DEV_VERSION_IND'] = '''
        puts("00");
    '''
c['GAPM_DEV_BDADDR_IND'] = '''
        puts("00");
    '''
c['GAPM_DEV_ADV_TX_POWER_IND'] = '''
        puts("00");
    '''
c['GAPM_DBG_MEM_INFO_IND'] = '''
        puts("00");
    '''
c['GAPM_PEER_NAME_IND'] = '''
        puts("00");
    '''
c['GAPM_RESOLV_ADDR_CMD'] = '''
        puts("00");
    '''
c['GAPM_ADDR_SOLVED_IND'] = '''
        puts("00");
    '''
c['GAPM_GEN_RAND_ADDR_CMD'] = '''
        puts("00");
    '''
c['GAPM_USE_ENC_BLOCK_CMD'] = '''
        puts("00");
    '''
c['GAPM_USE_ENC_BLOCK_IND'] = '''
        puts("00");
    '''
c['GAPM_GEN_RAND_NB_CMD'] = '''
        puts("00");
    '''
c['GAPM_GEN_RAND_NB_IND'] = '''
        puts("00");
    '''
c['GAPM_PROFILE_TASK_ADD_CMD'] = '''
        puts("00");
    '''
c['GAPM_PROFILE_ADDED_IND'] = '''
        puts("00");
    '''
c['GAPM_UNKNOWN_TASK_IND'] = '''
        puts("00");
    '''
c['GAPM_SUGG_DFLT_DATA_LEN_IND'] = '''
        puts("00");
    '''
c['GAPM_MAX_DATA_LEN_IND'] = '''
        puts("00");
    '''
c['GAPM_RAL_ADDR_IND'] = '''
        puts("00");
    '''
c['GAPM_SET_IRK_CMD'] = '''
        puts("00");
    '''
c['GAPM_LEPSM_REGISTER_CMD'] = '''
        puts("00");
    '''
c['GAPM_LEPSM_UNREGISTER_CMD'] = '''
        puts("00");
    '''
c['GAPM_LE_TEST_MODE_CTRL_CMD'] = '''
        puts("00");
    '''
c['GAPM_LE_TEST_END_IND'] = '''
        puts("00");
    '''
c['GAPM_ISO_STAT_IND'] = '''
        puts("00");
    '''
c['GAPM_GEN_DH_KEY_CMD'] = '''
        puts("00");
    '''
c['GAPM_GEN_DH_KEY_IND'] = '''
        puts("00");
    '''
c['GAPM_GET_PUB_KEY_CMD'] = '''
        puts("00");
    '''
c['GAPM_PUB_KEY_IND'] = '''
        puts("00");
    '''
c['GAPM_GET_RAL_ADDR_CMD'] = '''
        puts("00");
    '''
c['GAPM_LIST_SET_CMD'] = '''
        puts("00");
    '''
c['GAPM_LIST_SIZE_IND'] = '''
        puts("00");
    '''
c['GAPM_ACTIVITY_CREATE_CMD'] = '''
        struct gapm_activity_create_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_CREATE_CMD, TASK_GAPM, TASK_AHI, gapm_activity_create_cmd);
        m->operation = GAPM_CREATE_INIT_ACTIVITY;
        m->own_addr_type = GAPM_STATIC_ADDR; // Own address type @see enum gapm_own_addr
        dump(m);
    '''
c['GAPM_ACTIVITY_CREATE_SCAN_CMD'] = '''
        struct gapm_activity_create_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_CREATE_CMD, TASK_GAPM, TASK_AHI, gapm_activity_create_cmd);
        m->operation = GAPM_CREATE_SCAN_ACTIVITY;
        m->own_addr_type = GAPM_STATIC_ADDR; // Own address type @see enum gapm_own_addr
        dump(m);
    '''
c['GAPM_ACTIVITY_CREATE_INIT_CMD'] = '''
        struct gapm_activity_create_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_CREATE_CMD, TASK_GAPM, TASK_AHI, gapm_activity_create_cmd);
        m->operation = GAPM_CREATE_INIT_ACTIVITY;
        m->own_addr_type = GAPM_STATIC_ADDR; // Own address type @see enum gapm_own_addr
        dump(m);
    '''
c['GAPM_ACTIVITY_CREATE_INIT_PERIOD_SYNC_CMD'] = '''
        struct gapm_activity_create_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_CREATE_CMD, TASK_GAPM, TASK_AHI, gapm_activity_create_cmd);
        m->operation = GAPM_CREATE_PERIOD_SYNC_ACTIVITY;
        m->own_addr_type = GAPM_STATIC_ADDR; // Own address type @see enum gapm_own_addr
        dump(m);
    '''
c['GAPM_ACTIVITY_CREATE_ADV_CMD'] = '''
        struct gapm_activity_create_adv_cmd gapm_activity_create_adv_cmd = {
            .operation = GAPM_CREATE_ADV_ACTIVITY,
            .own_addr_type = GAPM_STATIC_ADDR,
            .adv_param = {
                .type = GAPM_ADV_TYPE_LEGACY, // @see enum gapm_adv_type
                .disc_mode = GAPM_ADV_MODE_GEN_DISC, // @see enum gapm_adv_disc_mode
                .prop = GAPM_ADV_PROP_UNDIR_CONN_MASK, // @see enum gapm_adv_prop
                .max_tx_pwr = 0,
                .filter_pol = ADV_ALLOW_SCAN_ANY_CON_ANY, // @see enum adv_filter_policy
                .peer_addr = {{0}, 0},
                .prim_cfg = { // primary advertising, @ref struct gapm_adv_prim_cfg
                    .adv_intv_min = 0x40, // unit of 625us
                    .adv_intv_max = 0x80,
                    .chnl_map = 0x07,
                    .phy = GAP_PHY_LE_1MBPS, // @ref enum gap_phy
                },
                .second_cfg = { // @ref struct gapm_adv_second_cfg
                    .max_skip = 4,
                    .phy = GAP_PHY_LE_1MBPS, // @see enum enum gap_phy
                    .adv_sid = 0x05,
                },
                .period_cfg = { // @ref struct gapm_adv_period_cfg
                    .adv_intv_min = 0x20, // unit of 1.25ms;
                    .adv_intv_max = 0x40,
                }
            },
        };
        struct gapm_activity_create_adv_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_CREATE_CMD, TASK_GAPM, TASK_AHI, gapm_activity_create_adv_cmd);
        memcpy(m, &gapm_activity_create_adv_cmd, sizeof(struct gapm_activity_create_adv_cmd));
        dump(m);
    '''
c['GAPM_ACTIVITY_START_CMD'] = '''
        struct gapm_activity_start_cmd gapm_activity_start_cmd = {
            .operation = GAPM_START_ACTIVITY,
            .actv_idx = 0,
            .u_param.adv_add_param = {
                .duration = 0, // unit of 10ms
                .max_adv_evt = 0,
            }
        };
        struct gapm_activity_start_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_START_CMD, TASK_GAPM, TASK_AHI, gapm_activity_start_cmd);
        memcpy(m, &gapm_activity_start_cmd, sizeof(struct gapm_activity_start_cmd));
        dump(m);
    '''
c['GAPM_ACTIVITY_START_ADV_CMD'] = '''
        struct gapm_activity_start_cmd gapm_activity_start_cmd = {
            .operation = GAPM_START_ACTIVITY,
            .actv_idx = 0,
            .u_param.adv_add_param = {
                .duration = 0, // unit of 10ms
                .max_adv_evt = 0,
            },
        };
        struct gapm_activity_start_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_START_CMD, TASK_GAPM, TASK_AHI, gapm_activity_start_cmd);
        memcpy(m, &gapm_activity_start_cmd, sizeof(struct gapm_activity_start_cmd));
        dump(m);
    '''
c['GAPM_ACTIVITY_START_SCAN_CMD'] = '''
        struct gapm_activity_start_cmd gapm_activity_start_cmd = {
            .operation = GAPM_START_ACTIVITY,
            .actv_idx = 0,
            .u_param.scan_param = {
                .type = GAPM_SCAN_TYPE_GEN_DISC, // @see enum gapm_scan_type
                .prop = GAPM_SCAN_PROP_PHY_1M_BIT | GAPM_SCAN_PROP_ACTIVE_1M_BIT, // @ref gapm_scan_prop
                .dup_filt_pol = 0,
                .scan_param_1m = { // struct gapm_scan_wd_op_param
                    .scan_intv = 0x80,
                    .scan_wd = 0x40,
                },
                .scan_param_coded = { // struct gapm_scan_wd_op_param
                    .scan_intv = 0xA0,
                    .scan_wd = 0x50,
                },
                .duration = 0, // unit of 10ms
                .period = 0, // unit of 1.28s
            },
        };
        struct gapm_activity_start_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_START_CMD, TASK_GAPM, TASK_AHI, gapm_activity_start_cmd);
        memcpy(m, &gapm_activity_start_cmd, sizeof(struct gapm_activity_start_cmd));
        dump(m);
    '''
c['GAPM_ACTIVITY_START_INIT_CMD'] = '''
        struct gapm_activity_start_cmd gapm_activity_start_cmd = {
            .operation = GAPM_START_ACTIVITY,
            .actv_idx = 0,
            .u_param.init_param = {
                .type = GAPM_INIT_TYPE_DIRECT_CONN_EST, // @see enum gapm_init_type
                .prop = GAPM_INIT_PROP_1M_BIT, // @ref gapm_init_prop
                .conn_to = 0, // unit of 10ms
                .scan_param_1m = { // struct gapm_scan_wd_op_param
                    .scan_intv = 0x80,
                    .scan_wd = 0x40,
                },
                .scan_param_coded = { // struct gapm_scan_wd_op_param
                    .scan_intv = 0xA0,
                    .scan_wd = 0x50,
                },
                .conn_param_1m = { // struct gapm_conn_param
                    .conn_intv_min = 0x30, // unit of 1.25ms, Allowed range is 7.5ms to 4s.
                    .conn_intv_max = 0x50,
                    .conn_latency = 0,
                    .supervision_to = 100, // unit of 10ms
                    .ce_len_min = 0, // unit of 625us
                    .ce_len_max = 0,
                },
                .conn_param_2m = { // struct gapm_conn_param
                    .conn_intv_min = 0x30, // unit of 1.25ms, Allowed range is 7.5ms to 4s.
                    .conn_intv_max = 0x50,
                    .conn_latency = 2,
                    .supervision_to = 120, // unit of 10ms
                    .ce_len_min = 0, // unit of 625us
                    .ce_len_max = 0,
                },
                .conn_param_coded = { // struct gapm_conn_param
                    .conn_intv_min = 0x30, // unit of 1.25ms, Allowed range is 7.5ms to 4s.
                    .conn_intv_max = 0x50,
                    .conn_latency = 4,
                    .supervision_to = 100, // unit of 10ms
                    .ce_len_min = 0, // unit of 625us
                    .ce_len_max = 0,
                },
                .peer_addr = { // struct gap_bdaddr
                    .addr = {0x66, 0x66, 0x66, 0x66, 0xbf, 0x01},
                    .addr_type = 0,
                },
            },
        };
        struct gapm_activity_start_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_START_CMD, TASK_GAPM, TASK_AHI, gapm_activity_start_cmd);
        memcpy(m, &gapm_activity_start_cmd, sizeof(struct gapm_activity_start_cmd));
        dump(m);
    '''
c['GAPM_ACTIVITY_START_PER_SYNC_CMD'] = '''
        struct gapm_activity_start_cmd gapm_activity_start_cmd = {
            .operation = GAPM_START_ACTIVITY,
            .actv_idx = 0,
            .u_param.per_sync_param = {
                .skip = 5,
                .sync_to = 200, // unit of 10ms between 100ms and 163.84s
                .type = GAPM_PER_SYNC_TYPE_GENERAL, // @see enum gapm_per_sync_type
                .adv_addr = { // struct gapm_period_adv_addr_cfg
                    .addr = {
                        .addr = {0},
                        .addr_type = 0,
                    },
                    .adv_sid = 0,
                },
            },
        };
        struct gapm_activity_start_cmd *m = KE_MSG_ALLOC(GAPM_ACTIVITY_START_CMD, TASK_GAPM, TASK_AHI, gapm_activity_start_cmd);
        memcpy(m, &gapm_activity_start_cmd, sizeof(struct gapm_activity_start_cmd));
        dump(m);
    '''
c['GAPM_ACTIVITY_STOP_CMD'] = '''
        puts("00");
    '''
c['GAPM_ACTIVITY_DELETE_CMD'] = '''
        struct gapm_activity_delete_cmd *m = KE_MSG_ALLOC_DYN(GAPM_ACTIVITY_DELETE_CMD, TASK_GAPM, TASK_AHI, gapm_activity_delete_cmd, 0);
        m->operation = GAPM_DELETE_ALL_ACTIVITIES; // GAPM_DELETE_ACTIVITY / GAPM_DELETE_ALL_ACTIVITIES
        m->actv_idx = 0;
        dump(m);
    '''
c['GAPM_ACTIVITY_CREATED_IND'] = '''
        puts("00");
    '''
c['GAPM_ACTIVITY_STOPPED_IND'] = '''
        puts("00");
    '''
c['GAPM_SET_ADV_DATA_CMD'] = '''
        const int length = 6;
        struct gapm_set_adv_data_cmd *m = KE_MSG_ALLOC_DYN(GAPM_SET_ADV_DATA_CMD, TASK_GAPM, TASK_AHI, gapm_set_adv_data_cmd, length);
        m->operation = GAPM_SET_ADV_DATA; // GAPM_SET_SCAN_RSP_DATA / GAPM_SET_PERIOD_ADV_DATA
        m->actv_idx = 0;
        m->length = length;
        memcpy(m->data, "\x02\x01\x06\x02\x09\x5f", length);
        dump(m);
    '''
c['GAPM_EXT_ADV_REPORT_IND'] = '''
        puts("00");
    '''
c['GAPM_SCAN_REQUEST_IND'] = '''
        puts("00");
    '''
c['GAPM_SYNC_ESTABLISHED_IND'] = '''
        puts("00");
    '''
c['GAPM_MAX_ADV_DATA_LEN_IND'] = '''
        puts("00");
    '''
c['GAPM_NB_ADV_SETS_IND'] = '''
        puts("00");
    '''
c['GAPM_DEV_TX_PWR_IND'] = '''
        puts("00");
    '''
c['GAPM_DEV_RF_PATH_COMP_IND'] = '''
        puts("00");
    '''
c['GAPM_UNKNOWN_MSG_IND'] = '''
        puts("00");
    '''
c['GAPC_CMP_EVT'] = '''
        puts("00");
    '''
c['GAPC_CONNECTION_REQ_IND'] = '''
        puts("00");
    '''
c['GAPC_CONNECTION_CFM'] = '''
        struct gapc_connection_cfm gapc_connection_cfm = {
            .lcsrk = {{0}}, // struct gap_sec_key
            .lsign_counter = 0,
            .rcsrk = {{0}}, // struct gap_sec_key
            .rsign_counter = 0,
            .auth = GAP_AUTH_REQ_NO_MITM_NO_BOND, // @see gap_auth
            .svc_changed_ind_enable = 0,
            .ltk_present = false,
        };
        struct gapc_connection_cfm *m = KE_MSG_ALLOC(GAPC_CONNECTION_CFM, TASK_GAPC, TASK_AHI, gapc_connection_cfm);
        memcpy(m, &gapc_connection_cfm, sizeof(struct gapc_connection_cfm));
        dump(m);
    '''
c['GAPC_DISCONNECT_IND'] = '''
        puts("00");
    '''
c['GAPC_DISCONNECT_CMD'] = '''
        puts("00");
    '''
c['GAPC_GET_INFO_CMD'] = '''
        puts("00");
    '''
c['GAPC_PEER_ATT_INFO_IND'] = '''
        puts("00");
    '''
c['GAPC_PEER_VERSION_IND'] = '''
        puts("00");
    '''
c['GAPC_PEER_FEATURES_IND'] = '''
        puts("00");
    '''
c['GAPC_CON_RSSI_IND'] = '''
        puts("00");
    '''
c['GAPC_GET_DEV_INFO_REQ_IND'] = '''
        puts("00");
    '''
c['GAPC_GET_DEV_INFO_CFM'] = '''
        puts("00");
    '''
c['GAPC_SET_DEV_INFO_REQ_IND'] = '''
        puts("00");
    '''
c['GAPC_SET_DEV_INFO_CFM'] = '''
        puts("00");
    '''
c['GAPC_PARAM_UPDATE_CMD'] = '''
        puts("00");
    '''
c['GAPC_PARAM_UPDATE_REQ_IND'] = '''
        puts("00");
    '''
c['GAPC_PARAM_UPDATE_CFM'] = '''
        struct gapc_param_update_cfm gapc_param_update_cfm = {
            .accept = true,
            .ce_len_min = 0x0000,
            .ce_len_max = 0xFFFF,
        };
        struct gapc_param_update_cfm *m = KE_MSG_ALLOC(GAPC_PARAM_UPDATE_CFM, TASK_GAPC, TASK_AHI, gapc_param_update_cfm);
        memcpy(m, &gapc_param_update_cfm, sizeof(struct gapc_param_update_cfm));
        dump(m);
    '''
c['GAPC_PARAM_UPDATED_IND'] = '''
        puts("00");
    '''
c['GAPC_BOND_CMD'] = '''
        puts("00");
    '''
c['GAPC_BOND_REQ_IND'] = '''
        puts("00");
    '''
c['GAPC_BOND_CFM'] = '''
        puts("00");
    '''
c['GAPC_BOND_IND'] = '''
        puts("00");
    '''
c['GAPC_ENCRYPT_CMD'] = '''
        puts("00");
    '''
c['GAPC_ENCRYPT_REQ_IND'] = '''
        puts("00");
    '''
c['GAPC_ENCRYPT_CFM'] = '''
        puts("00");
    '''
c['GAPC_ENCRYPT_IND'] = '''
        puts("00");
    '''
c['GAPC_SECURITY_CMD'] = '''
        puts("00");
    '''
c['GAPC_SECURITY_IND'] = '''
        puts("00");
    '''
c['GAPC_SIGN_COUNTER_IND'] = '''
        puts("00");
    '''
c['GAPC_CON_CHANNEL_MAP_IND'] = '''
        puts("00");
    '''
c['GAPC_SET_LE_PING_TO_CMD'] = '''
        puts("00");
    '''
c['GAPC_LE_PING_TO_VAL_IND'] = '''
        puts("00");
    '''
c['GAPC_LE_PING_TO_IND'] = '''
        puts("00");
    '''
c['GAPC_SET_LE_PKT_SIZE_CMD'] = '''
        puts("00");
    '''
c['GAPC_LE_PKT_SIZE_IND'] = '''
        puts("00");
    '''
c['GAPC_KEY_PRESS_NOTIFICATION_CMD'] = '''
        puts("00");
    '''
c['GAPC_KEY_PRESS_NOTIFICATION_IND'] = '''
        puts("00");
    '''
c['GAPC_SET_PHY_CMD'] = '''
        puts("00");
    '''
c['GAPC_LE_PHY_IND'] = '''
        puts("00");
    '''
c['GAPC_CHAN_SEL_ALGO_IND'] = '''
        puts("00");
    '''
c['GAPC_SET_PREF_SLAVE_LATENCY_CMD'] = '''
        puts("00");
    '''
c['GAPC_SET_PREF_SLAVE_EVT_DUR_CMD'] = '''
        puts("00");
    '''
c['GAPC_UNKNOWN_MSG_IND'] = '''
        puts("00");
    '''
c['GAPC_PER_ADV_SYNC_TRANS_CMD'] = '''
    #if CONFIG_PER_ADV_SYNC_TRANSFER
        struct gapc_per_adv_sync_trans_cmd gapc_per_adv_sync_trans_cmd = {
            .operation = GAPC_PER_ADV_SYNC_TRANS,
            .actv_idx = 0,
            .service_data = 0x6666,
        };
        struct gapc_per_adv_sync_trans_cmd *m = KE_MSG_ALLOC(GAPC_PER_ADV_SYNC_TRANS_CMD, TASK_GAPC, TASK_AHI, gapc_per_adv_sync_trans_cmd);
        memcpy(m, &gapc_per_adv_sync_trans_cmd, sizeof(struct gapc_per_adv_sync_trans_cmd));
        dump(m);
    #else
        puts("00");
    #endif
    '''

if __name__ == '__main__':
    res = code2stream(c)
    for cmd, stream in res.items():
        if len(stream) > 8:
            print('{:32s}: {}'.format(cmd, stream))
