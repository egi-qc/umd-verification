class {
    "arc_ce":
        arex_port                 => hiera("arc::params::arex_port"),
        manage_repository         => no,
        authorized_vos            => [
            'ops',
            'dteam',
            'ops.vo.ibergrid.eu'],
        cluster_cpudistribution   => ['16cpu:12'],
        cluster_description       => {
            'OSFamily'            => 'linux',
            'OSName'              => $::lsbdistid,
            'OSVersion'           => $::lsbdistrelease,
            'OSVersionName'       => $::lsbdistcodename,
            'CPUVendor'           => 'AMD',
            'CPUClockSpeed'       => '3100',
            'CPUModel'            => 'AMD Opteron(tm) Processor 4386',
            'NodeMemory'          => '1024',
            'totalcpus'           => '42',
        },
        cluster_owner             => 'UMD cluster owner',
        domain_name               => 'GOCDB-SITENAME',
        emi_repo_version          => '3',
        enable_firewall           => true,
        enable_glue1              => true,
        enable_glue2              => true,
        #glue_site_web             => hiera("bdii::params::siteweb"),
        #mail                      => hiera("bdii::params::siteemail"),
        #resource_location         => hiera("bdii::params::siteloc"),
        #resource_latitude         => hiera("bdii::params::sitelat"),
        #resource_longitude        => hiera("bdii::params::sitelong"),
        glue_site_web             => "http://es.wikipedia.org/wiki/Puerto_Hurraco",
        mail                      => "hermanos.izquierdo@example.org",
        resource_location         => "Puerto Hurraco",
        resource_latitude         => "38.6333",
        resource_longitude        => "-5.55",
        setup_RTEs                => true,
        use_argus                 => false,
        infosys_registration => {
            'clustertouk1' => {
              targethostname => 'index1.$::{domain}',
              targetport => '2170',
              targetsuffix => 'Mds-Vo-Name=sitename,o=grid',
              regperiod => '120',},

        #    'clustertouk2' => {
        #       targethostname => 'index2.gridpp.rl.ac.uk',
        #       targetport => '2135',
        #       targetsuffix => 'Mds-Vo-Name=UK,o=grid',
        #       regperiod => '120',}
        },
        #queue_defaults      = {
        #},
        queues              => {
            "batch" => {
                "queue_name" => "batch",
            }
        },
        lrms => "pbs",
}
