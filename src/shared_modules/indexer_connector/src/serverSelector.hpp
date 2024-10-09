/*
 * Securics content manager
 * Copyright (C) 2023-2024, RV Bionics Group SpA.
 * June 21, 2023.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#ifndef _SERVER_SELECTOR_HPP
#define _SERVER_SELECTOR_HPP

#include "monitoring.hpp"
#include "roundRobinSelector.hpp"
#include "secureCommunication.hpp"
#include <memory>
#include <string>

/**
 * @brief ServerSelector class.
 *
 */
class ServerSelector final : private RoundRobinSelector<std::string>
{
private:
    std::shared_ptr<Monitoring> monitoring;

public:
    ~ServerSelector() = default;

    /**
     * @brief Class constructor. Initializes Round Robin selector and monitoring.
     *
     * @param values Servers to be selected.
     * @param timeout Timeout for monitoring.
     * @param secureCommunication Object that provides secure communication.
     */
    explicit ServerSelector(const std::vector<std::string>& values,
                            const uint32_t timeout = INTERVAL,
                            const SecureCommunication& secureCommunication = {})
        : RoundRobinSelector<std::string>(values)
    {
        monitoring = std::make_shared<Monitoring>(values, timeout, secureCommunication);
    }

    /**
     * @brief Get next selected server.
     *
     * @return std::string Server address.
     */
    std::string getNext()
    {
        auto initialValue {RoundRobinSelector<std::string>::getNext()};
        auto retValue {initialValue};

        while (!monitoring->isAvailable(retValue))
        {
            retValue = RoundRobinSelector<std::string>::getNext();
            if (retValue.compare(initialValue) == 0)
            {
                throw std::runtime_error("No available server");
            }
        }
        return retValue;
    }
};

#endif // _SERVER_SELECTOR_HPP
