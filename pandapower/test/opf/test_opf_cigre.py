# -*- coding: utf-8 -*-

# Copyright (c) 2016-2025 by University of Kassel and Fraunhofer Institute for Energy Economics
# and Energy System Technology (IEE), Kassel. All rights reserved.

import numpy as np
import pytest

from pandapower.create import create_poly_cost
from pandapower.networks.cigre_networks import create_cigre_network_mv
from pandapower.run import runopp

try:
    import pandaplan.core.pplog as logging
except ImportError:
    import logging

logger = logging.getLogger(__name__)


def test_opf_cigre():
    """ Testing a  simple network with transformer for loading
    constraints with OPF using a generator """
    # create net
    net = create_cigre_network_mv(with_der="pv_wind")

    net.bus["max_vm_pu"] = 1.1
    net.bus["min_vm_pu"] = 0.9
    net.line["max_loading_percent"] = 200
    net.trafo["max_loading_percent"] = 100
    net.sgen["max_p_mw"] = net.sgen.sn_mva
    net.sgen["min_p_mw"] = 0
    net.sgen["max_q_mvar"] = 0.01
    net.sgen["min_q_mvar"] = -0.01
    net.sgen["controllable"] = True
    net.load["controllable"] = False
    net.sgen.loc[net.sgen.bus == 4, 'in_service'] = False
    net.sgen.loc[net.sgen.bus == 6, 'in_service'] = False
    net.sgen.loc[net.sgen.bus == 8, 'in_service'] = False
    net.sgen.loc[net.sgen.bus == 9, 'in_service'] = False

    # run OPF
    runopp(net)
    assert net["OPF_converged"]


def test_some_sgens_not_controllable():
    """ Testing a  simple network with transformer for loading
    constraints with OPF using a generator """
    # create net
    net = create_cigre_network_mv(with_der="pv_wind")

    net.bus["max_vm_pu"] = 1.1
    net.bus["min_vm_pu"] = 0.9
    net.line["max_loading_percent"] = 200
    net.trafo["max_loading_percent"] = 100
    net.sgen["max_p_mw"] = net.sgen.sn_mva
    net.sgen["min_p_mw"] = 0
    net.sgen["max_q_mvar"] = 0.01
    net.sgen["min_q_mvar"] = -0.01
    net.sgen["controllable"] = True
    net.load["controllable"] = False
    net.sgen.loc[net.sgen.bus == 4, "controllable"] = False
    net.sgen.loc[net.sgen.bus == 6, "controllable"] = False
    net.sgen.loc[net.sgen.bus == 8, "controllable"] = False
    net.sgen.loc[net.sgen.bus == 9, "controllable"] = False

    for sgen_idx, row in net["sgen"].iterrows():
        cost_sgen = create_poly_cost(net, sgen_idx, 'sgen', cp1_eur_per_mw=1.)
        net.poly_cost.cp1_eur_per_mw.at[cost_sgen] = 100

    # run OPF
    runopp(net, calculate_voltage_angles=False)
    assert net["OPF_converged"]
    # check if p_mw of non conrollable sgens are unchanged
    assert np.allclose(net.res_sgen.p_mw[~net.sgen.controllable], net.sgen.p_mw[~net.sgen.controllable])
    assert not np.allclose(net.res_sgen.p_mw[net.sgen.controllable], net.sgen.p_mw[net.sgen.controllable])


if __name__ == "__main__":
    pytest.main([__file__, "-xs"])
